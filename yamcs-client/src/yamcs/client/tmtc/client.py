import collections.abc
import datetime
import functools
import threading
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple, Union

from yamcs.client.core.context import Context
from yamcs.client.core.exceptions import YamcsError
from yamcs.client.core.futures import WebSocketSubscriptionFuture
from yamcs.client.core.helpers import (
    adapt_name_for_rest,
    to_argument_value,
    to_isostring,
    to_named_object_id,
    to_named_object_ids,
    to_server_time,
)
from yamcs.client.core.subscriptions import WebSocketSubscriptionManager
from yamcs.client.tmtc.model import (
    Alarm,
    AlarmRangeSet,
    AlarmUpdate,
    Calibrator,
    CommandHistory,
    ContainerData,
    IssuedCommand,
    MonitoredCommand,
    Packet,
    ParameterData,
    ParameterValue,
    ValueUpdate,
    VerificationConfig,
    _parse_alarm,
)
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.alarms import alarms_pb2, alarms_service_pb2
from yamcs.protobuf.commanding import commanding_pb2, commands_service_pb2
from yamcs.protobuf.mdb import mdb_pb2
from yamcs.protobuf.packets import packets_pb2, packets_service_pb2
from yamcs.protobuf.processing import mdb_override_service_pb2, processing_pb2
from yamcs.protobuf.pvalue import pvalue_pb2

__all__ = [
    "AlarmSubscription",
    "CommandConnection",
    "CommandHistorySubscription",
    "ContainerSubscription",
    "ParameterSubscription",
    "ProcessorClient",
]


class SequenceGenerator:
    """Static atomic counter."""

    _counter = 0
    _lock = threading.Lock()

    @classmethod
    def next(cls):
        with cls._lock:
            cls._counter += 1
            return cls._counter


def _wrap_callback_parse_parameter_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse ParameterData
    from a WebSocket data message
    """
    pb = processing_pb2.SubscribeParametersData()
    message.Unpack(pb)
    parameter_data = subscription._process(pb)
    if on_data and parameter_data:
        on_data(parameter_data)


def _wrap_callback_parse_packet_data(on_data, message):
    """
    Wraps an (optional) user callback to parse Packet
    from a WebSocket data message
    """
    pb = packets_pb2.TmPacketData()
    message.Unpack(pb)
    packet = Packet(pb)
    on_data(packet)


def _wrap_callback_parse_container_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse ContainerData
    from a WebSocket data message
    """
    pb = packets_service_pb2.ContainerData()
    message.Unpack(pb)
    container_data = subscription._process(pb)
    if on_data:
        on_data(container_data)


def _wrap_callback_parse_cmdhist_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse CommandHistoryEntry
    from a WebSocket data message
    """
    pb = commanding_pb2.CommandHistoryEntry()
    message.Unpack(pb)
    rec = subscription._process(pb)
    if on_data:
        on_data(rec)


def _wrap_callback_parse_alarm_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse Alarm data
    from a WebSocket data message
    """
    pb = alarms_pb2.AlarmData()
    message.Unpack(pb)
    alarm_update = AlarmUpdate(pb)
    subscription._process(alarm_update)
    if on_data:
        on_data(alarm_update)


def _build_value_proto(value):
    proto = yamcs_pb2.Value()
    if isinstance(value, bool):
        proto.type = proto.BOOLEAN
        proto.booleanValue = value
    elif isinstance(value, float):
        proto.type = proto.DOUBLE
        proto.doubleValue = value
    elif isinstance(value, int) and value > 2147483647:
        proto.type = proto.SINT64
        proto.sint64Value = value
    elif isinstance(value, int):
        proto.type = proto.SINT32
        proto.sint32Value = value
    elif isinstance(value, str):
        proto.type = proto.STRING
        proto.stringValue = value
    elif isinstance(value, bytes):
        proto.type = proto.BINARY
        proto.binaryValue = value
    elif isinstance(value, bytearray):
        proto.type = proto.BINARY
        proto.binaryValue = bytes(value)
    elif isinstance(value, datetime.datetime):
        proto.type = proto.TIMESTAMP
        proto.stringValue = to_isostring(value)
    elif isinstance(value, collections.abc.Mapping):
        proto.type = proto.AGGREGATE
        proto.aggregateValue.name.extend(value.keys())
        proto.aggregateValue.value.extend(
            [_build_value_proto(v) for v in value.values()]
        )
    elif isinstance(value, collections.abc.Sequence):
        proto.type = proto.ARRAY
        proto.arrayValue.extend([_build_value_proto(v) for v in value])
    else:
        raise YamcsError("Unrecognized type")
    return proto


def _set_range(ar, range, level):
    ar.level = level
    if range[0]:
        ar.minExclusive = range[0]
    if range[1]:
        ar.maxExclusive = range[1]


def _add_alarms(alarm_info, watch, warning, distress, critical, severe, min_violations):
    alarm_info.minViolations = min_violations

    if watch:
        ar = alarm_info.staticAlarmRange.add()
        _set_range(ar, watch, mdb_pb2.WATCH)
    if warning:
        ar = alarm_info.staticAlarmRange.add()
        _set_range(ar, warning, mdb_pb2.WARNING)
    if distress:
        ar = alarm_info.staticAlarmRange.add()
        _set_range(ar, distress, mdb_pb2.DISTRESS)
    if critical:
        ar = alarm_info.staticAlarmRange.add()
        _set_range(ar, critical, mdb_pb2.CRITICAL)
    if severe:
        ar = alarm_info.staticAlarmRange.add()
        _set_range(ar, severe, mdb_pb2.SEVERE)


def _add_calib(calib_info, type, data):
    type = type.lower()
    if type == Calibrator.POLYNOMIAL:
        calib_info.type = mdb_pb2.CalibratorInfo.POLYNOMIAL
        calib_info.polynomialCalibrator.coefficient.extend(data)
    elif type == Calibrator.SPLINE:
        calib_info.type = mdb_pb2.CalibratorInfo.SPLINE
        spline = mdb_pb2.SplineCalibratorInfo()
        for p in data:
            spi = spline.point.add()
            spi.raw = p[0]
            spi.calibrated = p[1]
    else:
        raise YamcsError("Unrecognized type")


class CommandHistorySubscription(WebSocketSubscriptionFuture):
    """
    Local object providing access to command history updates.

    This object buffers all received command history. This is needed
    to stitch together incremental command history events.

    If you expect to receive a lot of command history updates
    you should periodically clear local cache via ``clear_cache()``.
    In future work, we may add automated buffer management within
    configurable watermarks.

    .. warning::
        If command history updates are received for commands
        that are not currently in the local cache, the returned
        information may be incomplete.
    """

    def __init__(self, manager: WebSocketSubscriptionManager):
        super(CommandHistorySubscription, self).__init__(manager)
        self._cache: Dict[str, CommandHistory] = {}

    def clear_cache(self):
        """
        Clears local command history cache.
        """
        self._cache = {}

    def get_command_history(
        self, issued_command: IssuedCommand
    ) -> Optional[CommandHistory]:
        """
        Gets locally cached CommandHistory for the specified command.

        :param issued_command:
            object representing a previously issued command.
        """
        if issued_command.id in self._cache:
            return self._cache[issued_command.id]
        return None

    def _process(self, entry) -> CommandHistory:
        if entry.id in self._cache:
            cmdhist = self._cache[entry.id]
            cmdhist._update(entry.attr)
        else:
            cmdhist = CommandHistory(entry)
            self._cache[entry.id] = cmdhist

        return cmdhist


class ContainerSubscription(WebSocketSubscriptionFuture):
    """
    Local object providing access to container updates
    """

    def __init__(self, manager: WebSocketSubscriptionManager):
        super(ContainerSubscription, self).__init__(manager)
        self._cache: Dict[str, ContainerData] = {}
        """Container cache keyed by container name."""

    def get_container(self, name: str) -> ContainerData:
        """
        Returns the latest container of a specific name.

        :param name:
            Container name
        """
        return self._cache[name]

    def list_containers(self) -> List[ContainerData]:
        """
        Returns the latest container for each name.
        """
        return [self._cache[k] for k in self._cache]

    def _process(self, proto) -> ContainerData:
        container = ContainerData(proto)
        self._cache[container.name] = container
        return container


class ParameterSubscription(WebSocketSubscriptionFuture):
    """
    Local object representing a subscription of zero or more parameters.

    A subscription object stores the last received value of each
    subscribed parameter.
    """

    def __init__(self, manager: WebSocketSubscriptionManager):
        super(ParameterSubscription, self).__init__(manager)
        self._mapping = {}
        """Mapping from server-assigned identifier, to requested parameter"""

        self.value_cache: Dict[str, ParameterValue] = {}
        """Value cache keyed by parameter name."""

        self.delivery_count: int = 0
        """The number of parameter deliveries."""

        self._delivery_received = threading.Event()

    def add(
        self,
        parameters: Union[str, List[str]],
        abort_on_invalid: bool = True,
        send_from_cache: bool = True,
    ):
        """
        Add one or more parameters to this subscription.

        :param parameters:
            Parameter(s) to be added
        :param abort_on_invalid:
            If ``True`` one invalid parameter means any other parameter in the
            request will also not be added to the subscription.
        :param send_from_cache:
            If ``True`` the last processed parameter value is sent from
            parameter cache. When ``False`` only newly processed parameters
            are received.
        """
        if not parameters:
            return

        options = processing_pb2.SubscribeParametersRequest()
        options.action = processing_pb2.SubscribeParametersRequest.ADD
        options.abortOnInvalid = abort_on_invalid
        options.sendFromCache = send_from_cache
        options.id.extend(to_named_object_ids(parameters))

        self._manager.send(options)

    def remove(self, parameters: Union[str, List[str]]):
        """
        Remove one or more parameters from this subscription.

        :param parameters:
            Parameter(s) to be removed
        """
        if not parameters:
            return

        options = processing_pb2.SubscribeParametersRequest()
        options.action = processing_pb2.SubscribeParametersRequest.REMOVE
        options.id.extend(to_named_object_ids(parameters))

        self._manager.send(options)

    def get_value(self, parameter: str):
        """
        Returns the last value of a specific parameter from local cache.

        :param parameter:
            Parameter name.
        """
        return self.value_cache[parameter]

    def await_first_delivery(self, timeout: Optional[float] = None):
        """
        Wait for the first update of parameter values.

        :param timeout:
            The amount of seconds to wait.
        """
        if not self._delivery_received.wait(timeout=timeout):
            raise TimeoutError("Timed out.")

    def _process(self, pb):
        # Mapping is only set on the first reply, or whenever
        # the subscription is modifed. Store it in an internal
        # reference, so that we can find it back when receiving
        # future parameter_data updates.
        for k in pb.mapping:
            self._mapping[k] = pb.mapping[k]

        if pb.values:
            self.delivery_count += 1
            self._delivery_received.set()
            parameter_data = ParameterData(pb, self._mapping)
            for pval in parameter_data.parameters:
                self.value_cache[pval.name] = pval
            return parameter_data


class CommandConnection(WebSocketSubscriptionFuture):
    """
    Local object providing access to the acknowledgment progress
    of command updates.

    Only commands issued from this object are monitored.
    """

    def __init__(self, manager, tmtc_client: "ProcessorClient"):
        super(CommandConnection, self).__init__(manager)
        self._cmdhist_cache = {}
        self._command_cache = {}
        self._tmtc_client = tmtc_client

    def issue(
        self,
        command: str,
        args: Optional[Mapping[str, Any]] = None,
        *,
        dry_run: bool = False,
        comment: Optional[str] = None,
        verification: Optional[VerificationConfig] = None,
        stream: Optional[str] = None,
        extra: Optional[Mapping[str, Any]] = None,
        sequence_number: Optional[int] = None,
    ) -> MonitoredCommand:
        """
        Issue the given command

        :param command:
            Either a fully-qualified XTCE name or an alias in the
            format ``NAMESPACE/NAME``.
        :param args:
            Named arguments (if the command requires these).
        :param dry_run:
            If ``True`` the command is not actually issued. This can be used
            to test if the server would generate errors when preparing the
            command (for example because an argument is missing).
        :param comment:
            Comment attached to the command.
        :param verification:
            Overrides to the default verification handling of this command.
        :param stream:
            Override the stream on which the command should be sent out.

            .. versionadded:: 1.9.6
        :param extra:
            Extra command options for interpretation by non-core extensions
            (custom preprocessor, datalinks, command listeners). Note that
            Yamcs will refuse command options that it does now know about.
            Extensions should therefore register available options.
        :param sequence_number:
            Sequence number of this command. This is used to determine unicity
            of commands at the same time and coming from the same origin. If
            not set Yamcs will automatically assign a sequential number as if
            every submitted command is unique.

            .. versionadded:: 1.9.0

        :return:
            An object providing access to properties of the newly issued
            command and updated according to command history updates.
        """
        issued_command = self._tmtc_client.issue_command(
            command=command,
            args=args,
            dry_run=dry_run,
            comment=comment,
            verification=verification,
            stream=stream,
            extra=extra,
            sequence_number=sequence_number,
        )
        cmd = MonitoredCommand(issued_command._proto)

        self._command_cache[cmd.id] = cmd

        # It may be that we already received some cmdhist updates
        # before the http response returned.
        if cmd.id in self._cmdhist_cache:
            cmdhist = self._cmdhist_cache[cmd.id]
            cmd._process_cmdhist(cmdhist)

        return cmd

    def _process(self, entry):
        if entry.id in self._cmdhist_cache:
            cmdhist = self._cmdhist_cache[entry.id]
            cmdhist._update(entry.attr)
        else:
            cmdhist = CommandHistory(entry)
            self._cmdhist_cache[entry.id] = cmdhist

        command = self._command_cache.get(entry.id)
        if command:
            command._process_cmdhist(cmdhist)

        return cmdhist


class AlarmSubscription(WebSocketSubscriptionFuture):
    """
    Local object representing an alarm subscription.

    A subscription object stores the currently active
    alarms.
    """

    def __init__(self, manager):
        super(AlarmSubscription, self).__init__(manager)

        self._cache = {}
        """Value cache keyed by alarm name."""

    def get_alarm(self, name: str) -> Alarm:
        """
        Returns the alarm state associated with a specific named
        alarm from local cache.

        :param name:
            Fully-qualified name
        """
        return self._cache[name]

    def list_alarms(self) -> List[Alarm]:
        """
        Returns a snapshot of all active alarms.
        """
        return [self._cache[k] for k in self._cache]

    def _process(self, alarm_update):
        alarm = alarm_update.alarm
        if alarm.is_process_ok and not alarm.is_ok and alarm.is_acknowledged:
            del self._cache[alarm.name]
        else:
            self._cache[alarm.name] = alarm


class ProcessorClient:
    """Client object that groups operations linked to a specific processor."""

    def __init__(self, ctx: Context, instance: str, processor: str):
        super(ProcessorClient, self).__init__()
        self.ctx = ctx
        self._instance = instance
        self._processor = processor

    def get_parameter_value(
        self, parameter: str, from_cache: bool = True, timeout: float = 10
    ) -> Optional[ParameterValue]:
        """
        Retrieve the current value of the specified parameter.

        :param parameter:
            Either a fully-qualified XTCE name or an alias in the
            format ``NAMESPACE/NAME``.
        :param from_cache:
            If ``False`` this call will block until a
            fresh value is received on the processor.
            If ``True`` the server returns the latest
            value instead (which may be ``None``).
        :param timeout:
            The amount of seconds to wait for a fresh value.
            (ignored if ``from_cache=True``).
        """
        params = {
            "fromCache": from_cache,
            "timeout": int(timeout * 1000),
        }
        parameter = adapt_name_for_rest(parameter)
        url = f"/processors/{self._instance}/{self._processor}/parameters{parameter}"
        response = self.ctx.get_proto(url, params=params)
        proto = pvalue_pb2.ParameterValue()
        proto.ParseFromString(response.content)

        # Server returns ParameterValue with only 'id' set if no
        # value existed. Convert this to ``None``.
        if proto.HasField("rawValue") or proto.HasField("engValue"):
            return ParameterValue(proto)
        return None

    def get_parameter_values(
        self, parameters: List[str], from_cache: bool = True, timeout: float = 10
    ) -> List[Optional[ParameterValue]]:
        """
        Retrieve the current value of the specified parameter.

        :param parameters:
            List of parameter names. These may be
            fully-qualified XTCE name or an alias
            in the format ``NAMESPACE/NAME``.
        :param from_cache:
            If ``False`` this call will block until
            fresh values are received on the processor.
            If ``True`` the server returns the latest
            value instead (which may be ``None``).
        :param timeout:
            The amount of seconds to wait for a fresh
            values (ignored if ``from_cache=True``).
        :return:
            A list that matches the length and order of the requested
            list of parameters. Each entry contains either the
            returned parameter value, or ``None``.
        """
        req = processing_pb2.BatchGetParameterValuesRequest()
        req.id.extend(to_named_object_ids(parameters))
        req.fromCache = from_cache
        req.timeout = int(timeout * 1000)
        url = f"/processors/{self._instance}/{self._processor}/parameters:batchGet"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        proto = processing_pb2.BatchGetParameterValuesResponse()
        proto.ParseFromString(response.content)

        pvals = []
        for parameter_id in req.id:
            match = None
            for pval in proto.value:
                if pval.id == parameter_id:
                    match = pval
                    break
            pvals.append(ParameterValue(match) if match else None)
        return pvals

    def set_parameter_value(
        self,
        parameter: str,
        value: Any,
        generation_time: Optional[datetime.datetime] = None,
        expires_in: Optional[float] = None,
    ):
        """
        Sets the value of the specified parameter.

        :param parameter:
            Either a fully-qualified XTCE name or an alias in the format
            ``NAMESPACE/NAME``.
        :param value:
            The value to set.
        :param generation_time:
            Generation time of the value. If unset, Yamcs will assign the
            generation time.
        :param expires_in:
            How long before this value expires (in fractional seconds).
            If unset, the value does not expire.

            .. versionadded:: 1.9.1
               Compatible with Yamcs 5.8.8 onwards
        """
        self.set_parameter_values(
            {parameter: value}, generation_time=generation_time, expires_in=expires_in
        )

    def set_parameter_values(
        self,
        values: Mapping[str, Any],
        generation_time: Optional[datetime.datetime] = None,
        expires_in: Optional[float] = None,
    ):
        """
        Sets the value of multiple parameters.

        Values are specified with their native Python types. If you need
        to customize individual value properties, use
        :class:`.ValueUpdate` instead.

        The method arguments ``generation_time`` and ``expires_in`` can be used
        to specify a custom generation time for all values at once. This has
        lower priority than value-specific properties.

        If no generation time is specified at all, Yamcs will determine one.

        :param values:
            Values keyed by parameter name. This name can be either a
            fully-qualified XTCE name or an alias in the format
            ``NAMESPACE/NAME``.
        :param generation_time:
            Generation time of the values.
        :param expires_in:
            How long before this value expires (in fractional seconds).

            .. versionadded:: 1.9.1
               Compatible with Yamcs 5.8.8 onwards
        """
        req = processing_pb2.BatchSetParameterValuesRequest()
        for key in values:
            item = req.request.add()
            item.id.MergeFrom(to_named_object_id(key))

            value = values[key]
            value_time = generation_time
            value_expires_in = expires_in
            if isinstance(values[key], ValueUpdate):
                value = values[key].value
                if values[key].generation_time:
                    value_time = values[key].generation_time
                if values[key].expires_in is not None:
                    value_expires_in = values[key].expires_in

            item.value.MergeFrom(_build_value_proto(value))
            if value_time:
                item.generationTime.MergeFrom(to_server_time(value_time))
            if value_expires_in is not None:
                item.expiresIn = int(value_expires_in * 1000)
        url = f"/processors/{self._instance}/{self._processor}/parameters:batchSet"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def issue_command(
        self,
        command: str,
        args: Optional[Mapping[str, Any]] = None,
        *,
        dry_run: bool = False,
        comment: Optional[str] = None,
        verification: Optional[VerificationConfig] = None,
        stream: Optional[str] = None,
        extra: Optional[Mapping[str, Any]] = None,
        sequence_number: Optional[int] = None,
    ) -> IssuedCommand:
        """
        Issue the given command

        :param command:
            Either a fully-qualified XTCE name or an alias in the format
            ``NAMESPACE/NAME``.
        :param args:
            Named arguments (if the command requires any).
        :param dry_run:
            If ``True`` the command is not actually issued. This can be used
            to test if the server would generate errors when preparing the
            command (for example because an argument is missing).
        :param comment:
            Comment attached to the command.
        :param verification:
            Overrides to the default verification handling of this command.
        :param stream:
            Override the stream on which the command should be sent out.

            .. versionadded:: 1.9.6
        :param extra:
            Extra command options for interpretation by non-core
            extensions (custom preprocessor, datalinks, command listeners).
            Note that Yamcs will refuse command options that it does now know
            about. Extensions should therefore register available options.
        :param sequence_number:
            Sequence number of this command. This is used
            to determine unicity of commands at the same time and coming from
            the same origin. If not set Yamcs will automatically assign a
            sequential number as if every submitted command is unique.

            .. versionadded:: 1.9.0

        :return:
            An object providing access to properties of the newly issued
            command.
        """
        req = commands_service_pb2.IssueCommandRequest()
        req.sequenceNumber = SequenceGenerator.next()
        req.dryRun = dry_run
        if comment:
            req.comment = comment
        if sequence_number is not None:
            req.sequenceNumber = sequence_number
        if args:
            for key in args:
                req.args[key] = to_argument_value(args[key], force_string=True)
        if stream:
            req.stream = stream

        if verification:
            if verification._disable_all:
                req.disableVerifiers = True
            else:
                for verifier in verification._disabled:
                    req.verifierConfig[verifier].disable = True
                for verifier in verification._check_windows:
                    window = verification._check_windows[verifier]
                    if window["start"]:
                        start = int(window["start"] * 1000)
                        req.verifierConfig[verifier].checkWindow.timeToStartChecking = (
                            start
                        )
                    if window["stop"]:
                        stop = int(window["stop"] * 1000)
                        req.verifierConfig[verifier].checkWindow.timeToStopChecking = (
                            stop
                        )

        if extra:
            for key in extra:
                req.extra[key].MergeFrom(_build_value_proto(extra[key]))

        command = adapt_name_for_rest(command)
        url = f"/processors/{self._instance}/{self._processor}/commands{command}"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        proto = commands_service_pb2.IssueCommandResponse()
        proto.ParseFromString(response.content)
        return IssuedCommand(proto)

    def run_script(self, script: str, args: Optional[Union[str, List[str]]] = None):
        """
        Run a script.

        The script has access to the environment variables ``YAMCS_URL``,
        ``YAMCS_API_KEY``, ``YAMCS_INSTANCE`` and ``YAMCS_PROCESSOR``.

        :param script:
            This should be the relative path to an an executable file in one of
            the search locations. When unconfigured, the default search
            location is :file:`etc/scripts/` relative to the Yamcs working
            directory.

        :param args:
            Optional script arguments, passed verbatim in the command line.
        """

        # Local import to avoid circularity while the yamcs.client
        # package migration is going on.
        from yamcs.client.activities import ScriptActivity

        url = f"/activities/{self._instance}/activities"
        activity = ScriptActivity(script=script, args=args, processor=self._processor)
        req = activity._to_proto()
        self.ctx.post_proto(url, data=req.SerializeToString())

    def list_alarms(
        self,
        start: Optional[datetime.datetime] = None,
        stop: Optional[datetime.datetime] = None,
        include_pending=False,
    ) -> Iterable[Alarm]:
        """
        Lists the active alarms.

        Remark that this does not query the archive. Only active alarms on the
        current processor are returned.

        :param start:
            Minimum trigger time of the returned alarms (inclusive)
        :param stop:
            Maximum trigger time of the returned alarms (exclusive)
        :param include_pending:
            Whether to include alarms that are currently pending, because
            they have not reached the minimum violation count.

            .. versionadded:: 1.11.2
               Compatible with Yamcs 5.11.0 onwards
        """
        # TODO implement continuation token on server
        params: Dict[str, Any] = {"order": "asc"}
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)
        if include_pending:
            params["includePending"] = True
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        url = f"/processors/{self._instance}/{self._processor}/alarms"
        response = self.ctx.get_proto(path=url, params=params)
        message = alarms_service_pb2.ListAlarmsResponse()
        message.ParseFromString(response.content)
        alarms = getattr(message, "alarms")
        return iter([_parse_alarm(alarm) for alarm in alarms])

    def set_default_calibrator(self, parameter: str, type: Optional[str], data):
        """
        Apply a calibrator while processing raw values of the specified
        parameter. If there is already a default calibrator associated
        to this parameter, that calibrator gets replaced.

        .. note::

            Contextual calibrators take precedence over the default calibrator
            See :meth:`set_calibrators` for setting contextual calibrators.

        Two types of calibrators can be applied:

        * Polynomial calibrators apply a polynomial expression of the form:
          `y = a + bx + cx^2 + ...`.

          The `data` argument must be an array of floats ``[a, b, c, ...]``.

        * Spline calibrators interpolate the raw value between a set of points
          which represent a linear curve.

          The `data` argument must be an array of ``[x, y]`` points.

        :param parameter:
            Either a fully-qualified XTCE name or an alias in the format
            ``NAMESPACE/NAME``.
        :param type:
            One of ``polynomial`` or ``spline``.
        :param data:
            Calibration definition for the selected type.
        """
        req = mdb_override_service_pb2.UpdateParameterRequest()
        req.action = (
            mdb_override_service_pb2.UpdateParameterRequest.SET_DEFAULT_CALIBRATOR
        )
        if type:
            _add_calib(req.defaultCalibrator, type, data)

        parameter = adapt_name_for_rest(parameter)
        url = f"/mdb-overrides/{self._instance}/{self._processor}/parameters{parameter}"
        self.ctx.patch_proto(url, data=req.SerializeToString())

    def set_calibrators(self, parameter: str, calibrators: List[Calibrator]):
        """
        Apply an ordered set of calibrators for the specified parameter.
        This replaces existing calibrators (if any).

        Each calibrator may have a context, which indicates when it its
        effects may be applied. Only the first matching calibrator is
        applied.

        A calibrator with context ``None`` is the *default* calibrator.
        There can be only one such calibrator, and is always applied at
        the end when no other contextual calibrator was applicable.

        :param parameter:
            Either a fully-qualified XTCE name or an alias in the format
            ``NAMESPACE/NAME``.
        :param calibrators:
            List of calibrators (either contextual or not)
        """
        req = mdb_override_service_pb2.UpdateParameterRequest()
        req.action = mdb_override_service_pb2.UpdateParameterRequest.SET_CALIBRATORS
        for c in calibrators:
            if c.context:
                context_calib = req.contextCalibrator.add()
                context_calib.context = c.context
                calib_info = context_calib.calibrator
            else:
                calib_info = req.defaultCalibrator

            _add_calib(calib_info, c.type, c.data)

        parameter = adapt_name_for_rest(parameter)
        url = f"/mdb-overrides/{self._instance}/{self._processor}/parameters{parameter}"
        self.ctx.patch_proto(url, data=req.SerializeToString())

    def clear_calibrators(self, parameter: str):
        """
        Removes all calibrators for the specified parameter.
        """
        self.set_default_calibrator(parameter, None, None)
        self.set_calibrators(parameter, [])

    def reset_calibrators(self, parameter: str):
        """
        Reset all calibrators for the specified parameter to their original MDB value.
        """
        req = mdb_override_service_pb2.UpdateParameterRequest()
        req.action = mdb_override_service_pb2.UpdateParameterRequest.RESET_CALIBRATORS

        parameter = adapt_name_for_rest(parameter)
        url = f"/mdb-overrides/{self._instance}/{self._processor}/parameters{parameter}"
        self.ctx.patch_proto(url, data=req.SerializeToString())

    def set_default_alarm_ranges(
        self,
        parameter: str,
        watch: Optional[Tuple[Optional[float], Optional[float]]] = None,
        warning: Optional[Tuple[Optional[float], Optional[float]]] = None,
        distress: Optional[Tuple[Optional[float], Optional[float]]] = None,
        critical: Optional[Tuple[Optional[float], Optional[float]]] = None,
        severe: Optional[Tuple[Optional[float], Optional[float]]] = None,
        min_violations: int = 1,
    ):
        """
        Generate out-of-limit alarms for a parameter using the specified
        alarm ranges.

        This replaces any previous default alarms on this parameter.

        .. note::

            Contextual range sets take precedence over the default alarm
            ranges. See :meth:`set_alarm_range_sets` for setting contextual
            range sets.

        :param parameter:
            Either a fully-qualified XTCE name or an alias in the format
            ``NAMESPACE/NAME``.
        :param watch:
            Range expressed as a tuple ``(lo, hi)`` where lo and hi are
            assumed exclusive.
        :param warning:
            Range expressed as a tuple ``(lo, hi)`` where lo and hi are
            assumed exclusive.
        :param distress:
            Range expressed as a tuple ``(lo, hi)`` where lo and hi are
            assumed exclusive.
        :param critical:
            Range expressed as a tuple ``(lo, hi)`` where lo and hi are
            assumed exclusive.
        :param severe:
            Range expressed as a tuple ``(lo, hi)`` where lo and hi are
            assumed exclusive.
        :param min_violations:
            Minimum violations before an alarm is generated.
        """
        req = mdb_override_service_pb2.UpdateParameterRequest()
        req.action = mdb_override_service_pb2.UpdateParameterRequest.SET_DEFAULT_ALARMS
        if watch or warning or distress or critical or severe:
            _add_alarms(
                req.defaultAlarm,
                watch,
                warning,
                distress,
                critical,
                severe,
                min_violations,
            )

        parameter = adapt_name_for_rest(parameter)
        url = f"/mdb-overrides/{self._instance}/{self._processor}/parameters{parameter}"
        self.ctx.patch_proto(url, data=req.SerializeToString())

    def set_alarm_range_sets(self, parameter: str, sets: List[AlarmRangeSet]):
        """
        Apply an ordered list of alarm range sets for the specified
        parameter. This replaces existing alarm sets (if any).

        Each AlarmRangeSet may have a context, which indicates when
        its effects may be applied. Only the first matching set is
        applied.

        An AlarmRangeSet with context ``None`` represents the *default*
        set of alarm ranges.  There can be only one such set, and it is
        always applied at the end when no other set of contextual ranges
        is applicable.

        :param parameter:
            Either a fully-qualified XTCE name or an alias in the format
            ``NAMESPACE/NAME``.
        :param sets:
            List of range sets (either contextual or not)
        """
        req = mdb_override_service_pb2.UpdateParameterRequest()
        req.action = mdb_override_service_pb2.UpdateParameterRequest.SET_ALARMS
        for rs in sets:
            if rs.context:
                context_alarm = req.contextAlarm.add()
                context_alarm.context = rs.context
                alarm_info = context_alarm.alarm
            else:
                alarm_info = req.defaultAlarm

            _add_alarms(
                alarm_info,
                rs.watch,
                rs.warning,
                rs.distress,
                rs.critical,
                rs.severe,
                rs.min_violations,
            )

        parameter = adapt_name_for_rest(parameter)
        url = f"/mdb-overrides/{self._instance}/{self._processor}/parameters{parameter}"
        self.ctx.patch_proto(url, data=req.SerializeToString())

    def clear_alarm_ranges(self, parameter: str):
        """
        Removes all alarm limits for the specified parameter.
        """
        self.set_default_alarm_ranges(parameter)
        self.set_alarm_range_sets(parameter, [])

    def reset_alarm_ranges(self, parameter: str):
        """
        Reset all alarm limits for the specified parameter to their original
        MDB value.
        """
        req = mdb_override_service_pb2.UpdateParameterRequest()
        req.action = mdb_override_service_pb2.UpdateParameterRequest.RESET_ALARMS

        parameter = adapt_name_for_rest(parameter)
        url = f"/mdb-overrides/{self._instance}/{self._processor}/parameters{parameter}"
        self.ctx.patch_proto(url, data=req.SerializeToString())

    def acknowledge_alarm(
        self, alarm: str, sequence_number: int, comment: Optional[str] = None
    ):
        """
        Acknowledges a specific alarm.

        :param alarm:
            Alarm name
        :param sequence_number:
            Sequence number
        :param comment:
            Optional comment to associate with the state change.
        """
        name = adapt_name_for_rest(alarm)
        url = f"/processors/{self._instance}/{self._processor}"
        url += f"/alarms{name}/{sequence_number}:acknowledge"
        req = alarms_service_pb2.AcknowledgeAlarmRequest()
        if comment is not None:
            req.comment = comment
        self.ctx.post_proto(url, data=req.SerializeToString())

    def unshelve_alarm(
        self, alarm: str, sequence_number: int, comment: Optional[str] = None
    ):
        """
        Unshelve an alarm.

        :param alarm:
            Alarm name
        :param sequence_number:
            Sequence number
        :param comment:
            Optional comment to associate with the state change.
        """
        name = adapt_name_for_rest(alarm)
        url = f"/processors/{self._instance}/{self._processor}"
        url += f"/alarms{name}/{sequence_number}:unshelve"
        req = alarms_service_pb2.UnshelveAlarmRequest()
        self.ctx.post_proto(url, data=req.SerializeToString())

    def shelve_alarm(
        self, alarm: str, sequence_number: int, comment: Optional[str] = None
    ):
        """
        Shelve an alarm.

        :param alarm:
            Alarm name
        :param sequence_number:
            Sequence number
        :param comment:
            Optional comment to associate with the state change.
        """
        name = adapt_name_for_rest(alarm)
        url = f"/processors/{self._instance}/{self._processor}"
        url += f"/alarms{name}/{sequence_number}:shelve"
        req = alarms_service_pb2.ShelveAlarmRequest()
        if comment is not None:
            req.comment = comment
        self.ctx.post_proto(url, data=req.SerializeToString())

    def clear_alarm(
        self, alarm: str, sequence_number: int, comment: Optional[str] = None
    ):
        """
        Clear an alarm.

        .. note::
            If the reason that caused the alarm is still present, a new
            alarm instance will be generated.

        :param alarm:
            Alarm name
        :param sequence_number:
            Sequence number
        :param comment:
            Optional comment to associate with the state change.
        """
        name = adapt_name_for_rest(alarm)
        url = f"/processors/{self._instance}/{self._processor}"
        url += f"/alarms{name}/{sequence_number}:clear"
        req = alarms_service_pb2.ClearAlarmRequest()
        if comment is not None:
            req.comment = comment
        self.ctx.post_proto(url, data=req.SerializeToString())

    def create_command_connection(
        self,
        on_data: Optional[Callable[[CommandHistory], None]] = None,
        timeout: float = 60,
    ) -> CommandConnection:
        """
        Creates a connection for issuing multiple commands and
        following up on their acknowledgment progress.

        .. note::
            This is a convenience method that merges the functionalities
            of :meth:`create_command_history_subscription` with those of
            :meth:`issue_command`.

        :param on_data:
            Function that gets called with  :class:`.CommandHistory`
            updates. Only commands issued from this connection are
            reported.
        :param timeout:
            The amount of seconds to wait for the request to complete.

        :return:
            Future that can be used to manage the background websocket
            subscription
        """
        options = commands_service_pb2.SubscribeCommandsRequest()
        options.instance = self._instance
        options.processor = self._processor
        options.ignorePastCommands = True

        manager = WebSocketSubscriptionManager(
            self.ctx, topic="commands", options=options
        )

        # Represent subscription as a future
        subscription = CommandConnection(manager, self)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_cmdhist_data, subscription, on_data
        )

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def create_command_history_subscription(
        self,
        on_data: Optional[Callable[[CommandHistory], None]] = None,
        timeout: float = 60,
    ) -> CommandHistorySubscription:
        """
        Create a new command history subscription.

        :param on_data:
            Function that gets called with :class:`.CommandHistory` updates.
        :param timeout:
            The amount of seconds to wait for the request to complete.
        :return:
            Future that can be used to manage the background websocket
            subscription.
        """
        options = commands_service_pb2.SubscribeCommandsRequest()
        options.instance = self._instance
        options.processor = self._processor
        options.ignorePastCommands = True

        manager = WebSocketSubscriptionManager(
            self.ctx, topic="commands", options=options
        )

        # Represent subscription as a future
        subscription = CommandHistorySubscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_cmdhist_data, subscription, on_data
        )

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def create_packet_subscription(
        self,
        on_data: Callable[[Packet], None],
        stream: Optional[str] = None,
        timeout: float = 60,
    ) -> WebSocketSubscriptionFuture:
        """
        Create a new packet subscription.

        :param on_data:
            Function that gets called with :class:`.Packet` updates.
        :param stream:
            Stream to subscribe to.
        :param timeout:
            The amount of seconds to wait for the request to complete.
        :return:
            A Future that can be used to manage the background websocket
            subscription.
        """
        options = packets_service_pb2.SubscribePacketsRequest()
        options.instance = self._instance

        if stream:
            options.stream = stream
        else:
            options.processor = self._processor

        manager = WebSocketSubscriptionManager(
            self.ctx, topic="packets", options=options
        )

        # Represent subscription as a future
        subscription = WebSocketSubscriptionFuture(manager)

        wrapped_callback = functools.partial(_wrap_callback_parse_packet_data, on_data)

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def create_container_subscription(
        self,
        containers: Union[str, List[str]],
        on_data: Optional[Callable[[ContainerData], None]] = None,
        timeout: float = 60,
    ) -> ContainerSubscription:
        """
        Create a new container subscription.

        :param containers:
            Container names.
        :param on_data:
            Function that gets called with :class:`.ContainerData` updates.
        :param timeout:
            The amount of seconds to wait for the request to complete.
        :return:
            A Future that can be used to manage the background websocket
            subscription.
        """
        options = packets_service_pb2.SubscribeContainersRequest()
        options.instance = self._instance
        options.processor = self._processor
        if isinstance(containers, str):
            options.names.extend([containers])
        else:
            options.names.extend(containers)

        manager = WebSocketSubscriptionManager(
            self.ctx, topic="containers", options=options
        )

        # Represent subscription as a future
        subscription = ContainerSubscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_container_data, subscription, on_data
        )

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def create_parameter_subscription(
        self,
        parameters: Union[str, List[str]],
        on_data: Optional[Callable[[ParameterData], None]] = None,
        abort_on_invalid: bool = True,
        update_on_expiration: bool = False,
        send_from_cache: bool = True,
        timeout: float = 60,
    ) -> ParameterSubscription:
        """
        Create a new parameter subscription.

        :param parameters:
            Parameter names (or aliases).
        :param on_data:
            Function that gets called with :class:`.ParameterData` updates.
        :param abort_on_invalid:
            If ``True`` an error is generated when invalid parameters are
            specified.
        :param update_on_expiration:
            If ``True`` an update is received when a parameter value has
            become expired. This update holds the same value as the last
            known valid value, but with status set to ``EXPIRED``.
        :param send_from_cache:
            If ``True`` the last processed parameter value is sent from
            parameter cache. When ``False`` only newly processed parameters
            are received.
        :param timeout:
            The amount of seconds to wait for the request to complete.

        :return:
            A Future that can be used to manage the background websocket
            subscription.
        """
        options = processing_pb2.SubscribeParametersRequest()
        options.instance = self._instance
        options.processor = self._processor
        options.abortOnInvalid = abort_on_invalid
        options.updateOnExpiration = update_on_expiration
        options.sendFromCache = send_from_cache
        options.id.extend(to_named_object_ids(parameters))

        manager = WebSocketSubscriptionManager(
            self.ctx, topic="parameters", options=options
        )

        # Represent subscription as a future
        subscription = ParameterSubscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_parameter_data, subscription, on_data
        )

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def create_alarm_subscription(
        self,
        on_data: Optional[Callable[[AlarmUpdate], None]] = None,
        include_pending: bool = False,
        timeout: float = 60,
    ) -> AlarmSubscription:
        """
        Create a new alarm subscription.

        :param on_data:
            Function that gets called with :class:`.AlarmUpdate` updates.
        :param timeout:
            The amount of seconds to wait for the request to complete.
        :param include_pending:
            Whether to include alarms that are currently pending, because
            they have not reached the minimum violation count.

            .. versionadded:: 1.11.2
               Compatible with Yamcs 5.11.0 onwards

        :return:
            A Future that can be used to manage the background websocket
            subscription.
        """
        options = alarms_service_pb2.SubscribeAlarmsRequest()
        options.instance = self._instance
        options.processor = self._processor
        options.includePending = include_pending
        manager = WebSocketSubscriptionManager(
            self.ctx, topic="alarms", options=options
        )

        # Represent subscription as a future
        subscription = AlarmSubscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_alarm_data, subscription, on_data
        )

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def set_algorithm(self, parameter: str, text: str):
        """
        Change an algorithm text. Can only be peformed on JavaScript or Python
        algorithms.

        :param text:
            New algorithm text (as it would appear in excel or XTCE)
        :param parameter:
            Either a fully-qualified XTCE name or an alias in the format
            ``NAMESPACE/NAME``.
        """
        req = mdb_override_service_pb2.UpdateAlgorithmRequest()
        req.action = mdb_override_service_pb2.UpdateAlgorithmRequest.SET
        req.algorithm.text = text

        parameter = adapt_name_for_rest(parameter)
        url = f"/mdb-overrides/{self._instance}/{self._processor}/algorithms{parameter}"
        self.ctx.patch_proto(url, data=req.SerializeToString())

    def reset_algorithm(self, parameter: str):
        """
        Reset the algorithm text to its original definition from MDB

        :param parameter:
            Either a fully-qualified XTCE name or an alias in the format
            ``NAMESPACE/NAME``.
        """
        req = mdb_override_service_pb2.UpdateAlgorithmRequest()
        req.action = mdb_override_service_pb2.UpdateAlgorithmRequest.RESET

        parameter = adapt_name_for_rest(parameter)
        url = f"/mdb-overrides/{self._instance}/{self._processor}/algorithms{parameter}"
        self.ctx.patch_proto(url, data=req.SerializeToString())
