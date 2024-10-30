import binascii
import threading
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from yamcs.client.core.exceptions import TimeoutError, YamcsError
from yamcs.client.core.helpers import parse_server_time, parse_value, to_isostring
from yamcs.client.model import Event
from yamcs.protobuf.alarms import alarms_pb2
from yamcs.protobuf.pvalue import pvalue_pb2

__all__ = [
    "Acknowledgment",
    "Alarm",
    "AlarmRangeSet",
    "AlarmUpdate",
    "Calibrator",
    "CommandHistory",
    "ContainerData",
    "EventAlarm",
    "IssuedCommand",
    "MonitoredCommand",
    "Packet",
    "ParameterAlarm",
    "ParameterData",
    "ParameterValue",
    "ValueUpdate",
    "VerificationConfig",
]


def _parse_alarm(proto):
    """Converts a protobuf alarm to a specific Alarm implementation."""
    if proto.type == alarms_pb2.PARAMETER:
        return ParameterAlarm(proto)
    if proto.type == alarms_pb2.EVENT:
        return EventAlarm(proto)
    raise YamcsError("Unexpected type " + str(proto.type))


class Acknowledgment:
    def __init__(self, name, time, status, message):
        self.name = name
        """Name of this acknowledgment."""

        self.time = time
        """Last update time of this acknowledgment."""

        self.status = status
        """Status of this acknowlegment."""

        self.message = message
        """Message of this acknowledgment."""

    def is_terminated(self):
        return self.status and self.status != "SCHEDULED" and self.status != "PENDING"

    def __repr__(self):
        return f"{self.name}: {self.status}"

    def __str__(self):
        return self.__repr__()


class CommandHistory:
    def __init__(self, proto):
        self.generation_time: datetime = parse_server_time(proto.generationTime)
        """The generation time as set by Yamcs"""

        self._proto = proto
        self.attributes = {}
        self._update(proto.attr)

    @property
    def id(self) -> str:
        """
        A unique identifier for this command.
        """
        return self._proto.id

    @property
    def name(self) -> str:
        """Name of the command."""
        return self._proto.commandName

    @property
    def aliases(self) -> Dict[str, str]:
        """
        Aliases, keyed by namespace

        .. versionadded:: 1.9.2
           Compatible with Yamcs 5.8.4 onwards
        """
        return {key: self._proto.aliases[key] for key in self._proto.aliases}

    @property
    def origin(self) -> Optional[str]:
        """
        The origin of this command. Usually the IP address of the issuer.
        """
        if self._proto.HasField("origin"):
            return self._proto.origin
        return None

    @property
    def sequence_number(self) -> int:
        """
        The sequence number of this command. This is the sequence
        number assigned by the issuing client.
        """
        return self._proto.sequenceNumber

    @property
    def username(self) -> Optional[str]:
        """Username of the issuer."""
        return self.attributes.get("username")

    @property
    def assignments(self) -> Dict[str, Any]:
        """
        Argument assignments by name.

        This returns only explicit assignments set by the command
        issuer. To return all assignments, including ones that
        use their default values, use :attr:`all_assignments` instead.

        .. versionadded:: 1.9.2
        """
        args = {}
        for assignment in self._proto.assignments:
            if assignment.userInput:
                args[assignment.name] = parse_value(assignment.value)
        return args

    @property
    def all_assignments(self) -> Dict[str, Any]:
        """
        Argument assignments by name.

        .. versionadded:: 1.9.2
        """
        args = {}
        for assignment in self._proto.assignments:
            args[assignment.name] = parse_value(assignment.value)
        return args

    @property
    def source(self) -> str:
        """String representation of the command."""
        result = self.name + "("
        args = []
        for assignment in self._proto.assignments:
            if assignment.userInput:
                value = parse_value(assignment.value)
                if isinstance(value, str):
                    value = '"' + value + '"'
                elif isinstance(value, bytes) or isinstance(value, bytearray):
                    value = '"' + binascii.hexlify(value).decode("ascii") + '"'
                elif isinstance(value, datetime):
                    value = '"' + to_isostring(value) + '"'
                args.append(assignment.name + ": " + str(value))
        result += ", ".join(args)
        result += ")"
        return result

    @property
    def unprocessed_binary(self):
        """
        Binary representation before postprocessing.

        .. versionadded:: 1.9.2
        """
        if self._proto.HasField("unprocessedBinary"):
            return self._proto.unprocessedBinary
        return None

    @property
    def binary(self):
        """Binary representation of the command."""
        return self.attributes.get("binary")

    def is_complete(self) -> bool:
        """
        Returns whether this command is complete. A command
        can be completed, yet still failed.
        """
        ack = self._assemble_ack("CommandComplete")
        return (ack is not None) and (ack.status == "OK" or ack.status == "NOK")

    def is_success(self) -> bool:
        """
        Returns True if the command has completed successfully.
        """
        ack = self._assemble_ack("CommandComplete")
        return (ack is not None) and ack.status == "OK"

    def is_failure(self) -> bool:
        """
        Returns True if the command has completed, but failed.
        """
        ack = self._assemble_ack("CommandComplete")
        return (ack is not None) and ack.status == "NOK"

    @property
    def error(self) -> Optional[str]:
        """Error message in case the command failed."""
        ack = self._assemble_ack("CommandComplete")
        if ack and ack.status == "NOK":
            return ack.message
        return None

    @property
    def comment(self) -> Optional[str]:
        """Optional user comment attached when issuing the command."""
        return self.attributes.get("comment")

    @property
    def acknowledgments(self) -> Dict[str, Acknowledgment]:
        """
        All acknowledgments by name.

        :return:
            Acknowledgments keyed by name.
        """
        acks = {}
        for name, _ in self.attributes.items():
            if name.startswith("CommandComplete"):
                continue
            if name.startswith("TransmissionConstraints"):
                continue
            if name.endswith("_Status"):
                ack = self._assemble_ack(name[:-7])
                if ack:
                    acks[ack.name] = ack

        return acks

    def _assemble_ack(self, name: str) -> Optional[Acknowledgment]:
        time = self.attributes.get(name + "_Time")
        status = self.attributes.get(name + "_Status")
        message = self.attributes.get(name + "_Message")
        if time and status:
            return Acknowledgment(name, time, status, message)
        return None

    def _update(self, proto):
        # Copy-on-write to avoid mutation error on the exposed attributes field
        copy = self.attributes.copy()
        for attr in proto:
            value = parse_value(attr.value)
            copy[attr.name] = value
        self.attributes = copy

    def __str__(self):
        acks = ", ".join(ack.__repr__() for _, ack in self.acknowledgments.items())
        return f"{self.name} [{acks}]"


class IssuedCommand:
    def __init__(self, proto):
        self._proto = proto

    @property
    def id(self) -> str:
        """
        A unique identifier for this command.
        """
        return self._proto.id

    @property
    def name(self) -> str:
        """
        The fully-qualified name of this command.
        """
        return self._proto.commandName

    @property
    def aliases(self) -> Dict[str, str]:
        """
        Aliases, keyed by namespace

        .. versionadded:: 1.9.2
           Compatible with Yamcs 5.8.4 onwards
        """
        return {key: self._proto.aliases[key] for key in self._proto.aliases}

    @property
    def generation_time(self) -> datetime:
        """
        The generation time as set by Yamcs.
        """
        return parse_server_time(self._proto.generationTime)

    @property
    def username(self) -> str:
        """The username of the issuer."""
        return self._proto.username

    @property
    def assignments(self) -> Dict[str, Any]:
        """
        Argument assignments by name.

        This returns only explicit assignments set by the command
        issuer. To return all assignments, including ones that
        use their default values, use :attr:`all_assignments` instead.

        .. versionadded:: 1.9.2
        """
        args = {}
        for assignment in self._proto.assignments:
            if assignment.userInput:
                args[assignment.name] = parse_value(assignment.value)
        return args

    @property
    def all_assignments(self) -> Dict[str, Any]:
        """
        Argument assignments by name.

        .. versionadded:: 1.9.2
        """
        args = {}
        for assignment in self._proto.assignments:
            args[assignment.name] = parse_value(assignment.value)
        return args

    @property
    def queue(self) -> Optional[str]:
        """The name of the queue that this command was assigned to."""
        if self._proto.HasField("queue"):
            return self._proto.queue
        return None

    @property
    def origin(self) -> Optional[str]:
        """
        The origin of this command. Usually the IP address of the issuer.
        """
        if self._proto.HasField("origin"):
            return self._proto.origin
        return None

    @property
    def sequence_number(self):
        """
        The sequence number of this command. This is the sequence
        number assigned by the issuing client.
        """
        if self._proto.HasField("sequenceNumber"):
            return self._proto.sequenceNumber
        return None

    @property
    def source(self):
        """String representation of this command."""
        result = None
        if self.name:
            result = self.name + "("
            args = []
            for assignment in self._proto.assignments:
                if assignment.userInput:
                    value = parse_value(assignment.value)
                    if isinstance(value, str):
                        value = '"' + value + '"'
                    elif isinstance(value, bytes) or isinstance(value, bytearray):
                        value = '"' + binascii.hexlify(value).decode("ascii") + '"'
                    elif isinstance(value, datetime):
                        value = '"' + to_isostring(value) + '"'
                    args.append(assignment.name + ": " + str(value))
            result += ", ".join(args)
            result += ")"

        return result

    @property
    def hex(self):
        """Hexadecimal string representation of this command."""
        if self._proto.HasField("binary"):
            return binascii.hexlify(self._proto.binary).decode("ascii")
        return None

    @property
    def unprocessed_binary(self):
        """
        Binary representation before postprocessing.

        .. versionadded:: 1.8.4
           Compatible with Yamcs 5.7.0 onwards
        """
        if self._proto.HasField("unprocessedBinary"):
            return self._proto.unprocessedBinary
        return None

    @property
    def binary(self):
        """Binary representation of this command."""
        if self._proto.HasField("binary"):
            return self._proto.binary
        return None

    def __str__(self):
        return f"{self.generation_time} {self.source}"


class VerificationConfig:
    """
    Contains overrides to the default verification handling of Yamcs.
    """

    def __init__(self):
        self._disabled = []
        self._disable_all = False
        self._check_windows = {}

    def disable(self, verifier: Optional[str] = None):
        """
        Disable verification.

        :param verifier:
            Name of a specific verifier to disable. If unspecified
            all verifiers are disabled.
        """
        if verifier:
            self._disabled.append(verifier)
        else:
            self._disable_all = True

    def modify_check_window(
        self, verifier: str, start: Optional[float] = None, stop: Optional[float] = None
    ):
        """
        Set or override the check window.

        Depending on the Mission Database configuration,
        the time may be relative to either the command release
        or a preceding verifier.

        :param verifier:
            Name of the verifier
        :param start:
            Window start time (relative, in seconds)
        :param stop:
            Window stop time (relative, in seconds)
        """
        self._check_windows[verifier] = {"start": start, "stop": stop}


class MonitoredCommand(IssuedCommand):
    """
    Represent an instance of an issued command that is updated
    throughout the acknowledgment process.

    Objects of this class are owned by a :class:`.CommandConnection` instance.
    """

    def __init__(self, proto):
        super(MonitoredCommand, self).__init__(proto)
        self._cmdhist = None
        self._completed = threading.Event()
        self._ack_events = {}

    def _process_cmdhist(self, cmdhist):
        self._cmdhist = cmdhist
        if self.is_complete():
            self._completed.set()
        for name, ack in self.acknowledgments.items():
            event = self._ack_events.setdefault(name, threading.Event())
            if ack.is_terminated():
                event.set()

    @property
    def attributes(self) -> Dict[str, Any]:
        if self._cmdhist:
            return self._cmdhist.attributes
        return {}

    def is_complete(self) -> bool:
        """
        Returns whether this command is complete. A command
        can be completed, yet still failed.

        Use :meth:`await_complete` to wait until this information
        is available.
        """
        ack = self._assemble_ack("CommandComplete")
        return (ack is not None) and (ack.status == "OK" or ack.status == "NOK")

    def is_success(self) -> bool:
        """
        Returns True if this command was completed successfully.

        Use :meth:`await_complete` to wait until this information
        is available.
        """
        ack = self._assemble_ack("CommandComplete")
        return (ack is not None) and ack.status == "OK"

    def is_failure(self) -> bool:
        """
        Returns True if the command has completed, but failed.

        Use :meth:`await_complete` to wait until this information
        is available.

        .. versionadded:: 1.8.6
        """
        ack = self._assemble_ack("CommandComplete")
        return (ack is not None) and ack.status == "NOK"

    def await_complete(self, timeout: Optional[float] = None):
        """
        Wait for the command to be `completed`. Afterwards use
        :meth:`is_success` or :meth:`is_failure` to determine
        whether the command was successful or not.

        .. note::

            Yamcs cannot determine completion unless the command has
            an appropriate verifier configured in the Yamcs MDB.

            When no such verifier is present, this method will never
            return (or timeout).

        :param timeout:
            The amount of seconds to wait.
        """
        self._wait_on_signal(self._completed, timeout)

    def await_acknowledgment(
        self, name: str, timeout: Optional[float] = None
    ) -> Acknowledgment:
        """
        Waits for the result of a specific acknowledgment.

        :param name:
            The name of the acknowledgment. Standard names are
            ``Acknowledge_Queued``, ``Acknowledge_Released``
            and ``Acknowledge_Sent``. Others depend on
            specific link types.
        :param timeout:
            The amount of seconds to wait.
        """
        event = self._ack_events.setdefault(name, threading.Event())
        self._wait_on_signal(event, timeout)
        ack = self.acknowledgments.get(name)
        assert ack is not None
        return ack

    def _wait_on_signal(self, event: threading.Event, timeout: Optional[float] = None):
        if not event.wait(timeout=timeout):
            # Remark that a timeout does *not* mean that the underlying
            # work is canceled.
            raise TimeoutError("Timed out.")

    @property
    def error(self) -> Optional[str]:
        """
        Error message in case the command failed.

        This information is only available when the command has failed
        to complete. (:meth:`is_failure` returns `True`).
        """
        ack = self._assemble_ack("CommandComplete")
        if ack and ack.status == "NOK":
            return ack.message
        return None

    @property
    def comment(self) -> Optional[str]:
        """Optional user comment attached when issuing the command."""
        return self.attributes.get("comment")

    @property
    def acknowledgments(self) -> Dict[str, Acknowledgment]:
        """
        All acknowledgments by name.

        :return:
            Acknowledgments keyed by name.
        """
        acks = {}
        for name, _ in self.attributes.items():
            if name.startswith("CommandComplete"):
                continue
            if name.startswith("TransmissionConstraints"):
                continue
            if name.endswith("_Status"):
                ack = self._assemble_ack(name[:-7])
                if ack:
                    acks[ack.name] = ack

        return acks

    def _assemble_ack(self, name: str) -> Optional[Acknowledgment]:
        time = self.attributes.get(name + "_Time")
        status = self.attributes.get(name + "_Status")
        message = self.attributes.get(name + "_Message")
        if time and status:
            return Acknowledgment(name, time, status, message)
        return None

    def _update(self, proto):
        # Copy-on-write to avoid mutation error on the exposed attributes field
        copy = self.attributes.copy()
        for attr in proto:
            value = parse_value(attr.value)
            copy[attr.name] = value
        self.attributes = copy

    def __str__(self):
        acks = ", ".join(ack.__repr__() for _, ack in self.acknowledgments.items())
        return f"{self.name} [{acks}]"


class AlarmUpdate:
    """
    Object received through callbacks when subscribing to alarm updates.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def update_type(self) -> str:
        """Type of update."""
        return alarms_pb2.AlarmNotificationType.Name(self._proto.type)

    @property
    def alarm(self) -> "Alarm":
        """
        Latest alarm state.
        """
        return _parse_alarm(self._proto)

    def __str__(self):
        return f"[{self.update_type}] {self.alarm}"


class Alarm(ABC):
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Fully-qualified name of the source of this alarm."""
        if self._proto.id.HasField("namespace"):
            return self._proto.id.namespace + "/" + self._proto.id.name
        return self._proto.id.name

    @property
    def trigger_time(self) -> datetime:
        """
        Processor time when the alarm was triggered.
        """
        return parse_server_time(self._proto.triggerTime)

    @property
    def update_time(self) -> datetime:
        """
        Processor time when the alarm was last updated.
        """
        if self._proto.HasField("updateTime"):
            return parse_server_time(self._proto.updateTime)
        return None

    @property
    def severity(self) -> str:
        return alarms_pb2.AlarmSeverity.Name(self._proto.severity)

    @property
    def sequence_number(self) -> int:
        """
        Sequence number for this specific alarm instance. This allows ensuring
        that operations (such as acknowledgment) are done on the expected alarm
        instance.
        """
        return self._proto.seqNum

    @property
    def is_ok(self) -> bool:
        """
        True if this alarm is currently 'inactive'.

        For a non-latching alarm this is identical to :meth:`is_process_ok`. A
        latching alarm is only OK if it has returned to normal and was
        acknowledged.
        """
        return not self._proto.triggered

    @property
    def is_process_ok(self) -> bool:
        """
        True if the process that caused this alarm is OK. For example:
        parameter back within limits.

        For a non-latching alarm this is identical to :meth:`is_ok`.
        """
        return self._proto.processOK

    @property
    def is_latching(self) -> bool:
        """
        True if this is a latching alarm. A latching alarm returns to
        normal only when the operator resets it
        """
        return self._proto.HasField("latching") and self._proto.latching

    @property
    def is_latched(self) -> bool:
        """
        True if this alarm is currently latched.
        """
        return self.is_latching and self.is_process_ok and not self.is_ok

    @property
    def is_acknowledged(self) -> bool:
        """True if this alarm has been acknowledged."""
        return self._proto.acknowledged

    @property
    def acknowledged_by(self) -> Optional[str]:
        """Username of the acknowledger."""
        if self.is_acknowledged and self._proto.acknowledgeInfo.HasField(
            "acknowledgedBy"
        ):
            return self._proto.acknowledgeInfo.acknowledgedBy
        return None

    @property
    def acknowledge_message(self) -> Optional[str]:
        """Comment provided when acknowledging the alarm."""
        if self.is_acknowledged and self._proto.acknowledgeInfo.HasField(
            "acknowledgeMessage"
        ):
            return self._proto.acknowledgeInfo.acknowledgeMessage
        return None

    @property
    def acknowledge_time(self) -> Optional[datetime]:
        """
        Processor time when the alarm was acknowledged.
        """
        if self.is_acknowledged and self._proto.acknowledgeInfo.HasField(
            "acknowledgeTime"
        ):
            return parse_server_time(self._proto.acknowledgeInfo.acknowledgeTime)
        return None

    @property
    def is_shelved(self) -> bool:
        """True if this alarm has been shelved."""
        return self._proto.HasField("shelveInfo")

    @property
    def violation_count(self) -> int:
        """
        Number of violating samples while this alarm is active.
        """
        return self._proto.violations

    @property
    def count(self) -> int:
        """
        Total number of samples while this alarm is active.
        """
        return self._proto.count

    def __str__(self):
        return f"{self.name} ({self.violation_count} violations)"


class ParameterAlarm(Alarm):
    """
    An alarm triggered by a parameter that went out of limits.
    """

    @property
    def trigger_value(self) -> "ParameterValue":
        """
        Parameter value that originally triggered the alarm
        """
        return ParameterValue(self._proto.parameterDetail.triggerValue)

    @property
    def most_severe_value(self) -> "ParameterValue":
        """
        First parameter value that invoked the highest severity
        level of this alarm.
        """
        return ParameterValue(self._proto.parameterDetail.mostSevereValue)

    @property
    def current_value(self) -> "ParameterValue":
        """
        Latest parameter value for this alarm.
        """
        return ParameterValue(self._proto.parameterDetail.currentValue)


class EventAlarm(Alarm):
    """
    An alarm triggered by an event.
    """

    @property
    def trigger_event(self) -> Event:
        """
        Event that originally triggered the alarm
        """
        return Event(self._proto.eventDetail.triggerEvent)

    @property
    def most_severe_event(self) -> Event:
        """
        First event that invoked the highest severity level
        of this alarm
        """
        return Event(self._proto.eventDetail.mostSevereEvent)

    @property
    def current_event(self) -> Event:
        """
        Latest event for this alarm
        """
        return Event(self._proto.eventDetail.currentEvent)


class ParameterValue:
    def __init__(self, proto, id=None):
        self._proto = proto
        self._id = id or proto.id

    @property
    def name(self) -> str:
        """
        An identifying name for the parameter value. Typically this is the
        fully-qualified XTCE name, but it may also be an alias depending
        on how the parameter update was requested.
        """
        if self._id.namespace:
            return self._id.namespace + "/" + self._id.name
        return self._id.name

    @property
    def generation_time(self) -> datetime:
        """
        The time when the parameter was generated. If the parameter
        was extracted from a packet, this usually returns the packet time.
        """
        return parse_server_time(self._proto.generationTime)

    @property
    def reception_time(self) -> Optional[datetime]:
        """
        The time when the parameter value was received by Yamcs.
        """
        if self._proto.HasField("acquisitionTime"):
            return parse_server_time(self._proto.acquisitionTime)
        return None

    @property
    def validity_duration(self) -> Optional[timedelta]:
        """
        How long this parameter value is valid.

        .. note: There is also an option when subscribing to get updated when
                 the parameter values expire.
        """
        if self._proto.HasField("expireMillis"):
            return timedelta(milliseconds=self._proto.expireMillis)
        return None

    @property
    def raw_value(self):
        """
        The raw (uncalibrated) value.
        """
        if self._proto.HasField("rawValue"):
            return parse_value(self._proto.rawValue)
        return None

    @property
    def eng_value(self):
        """
        The engineering (calibrated) value.
        """
        if self._proto.HasField("engValue"):
            return parse_value(self._proto.engValue)
        return None

    @property
    def monitoring_result(self) -> str:
        if self._proto.HasField("monitoringResult"):
            return pvalue_pb2.MonitoringResult.Name(self._proto.monitoringResult)
        return None

    @property
    def range_condition(self) -> Optional[str]:
        """
        If the value is out of limits, this indicates ``LOW`` or ``HIGH``.
        """
        if self._proto.HasField("rangeCondition"):
            return pvalue_pb2.RangeCondition.Name(self._proto.rangeCondition)
        return None

    @property
    def validity_status(self) -> str:
        if self._proto.HasField("acquisitionStatus"):
            return pvalue_pb2.AcquisitionStatus.Name(self._proto.acquisitionStatus)
        return None

    def __str__(self):
        line = f"{self.generation_time} {self.name} {self.raw_value} {self.eng_value}"
        if self.monitoring_result:
            line += " [" + self.monitoring_result + "]"
        return line


class ParameterData:
    def __init__(self, proto, mapping=None):
        self._proto = proto
        self._mapping = mapping

        self._pvals = {}
        if self._mapping is None:  # ParameterData proto
            for pval_pb in proto.parameter:
                pval = ParameterValue(pval_pb)
                self._pvals[pval.name] = pval
        else:  # SubscribeParametersData proto
            for pval_pb in self._proto.values:
                id = self._mapping[pval_pb.numericId]
                pval = ParameterValue(pval_pb, id=id)
                self._pvals[pval.name] = pval

    def __iter__(self):
        for pval in self._pvals.values():
            yield pval

    def get_value(self, parameter: str) -> Optional[ParameterValue]:
        """
        Returns the value of a specific parameter.
        Or ``None`` if the parameter is not included in
        this update.

        :param parameter:
            Parameter name.
        """
        return self._pvals.get(parameter)

    @property
    def parameters(self) -> List[ParameterValue]:
        return list(self._pvals.values())

    def __str__(self):
        return self.parameters.__str__()


class Calibrator:
    """
    A calibrator that may be applied to a numeric raw value.

    Two types of calibrators can be applied:

    * Polynomial calibrators apply a polynomial expression of the form:
        `y = a + bx + cx^2 + ...`.

        The `data` argument must be an array of floats ``[a, b, c, ...]``.

    * Spline calibrators interpolate the raw value between a set of points
        which represent a linear curve.

        The `data` argument must be an array of ``[x, y]`` points.
    """

    POLYNOMIAL = "polynomial"
    SPLINE = "spline"

    def __init__(self, context: str, type: str, data):
        """
        :param context:
            Condition under which this calibrator may be
            applied. The value ``None`` indicates the
            default calibrator which is only applied if
            no contextual calibrators match.
        :param type:
            One of ``polynomial`` or ``spline``.
        :param data:
            Calibration definition for the selected type.
        """
        self.context = context
        self.type = type
        self.data = data


class ContainerData:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """
        The name of the container.
        """
        return self._proto.name

    @property
    def generation_time(self) -> datetime:
        """
        The time when this container's packet was generated (packet time).
        """
        return parse_server_time(self._proto.generationTime)

    @property
    def reception_time(self) -> datetime:
        """
        The time when this container's packet was received by Yamcs.
        """
        return parse_server_time(self._proto.receptionTime)

    @property
    def binary(self):
        """
        Raw binary
        """
        if self._proto.HasField("binary"):
            return self._proto.binary
        return None

    def __str__(self):
        return f"{self.generation_time} ({self.name})"


class Packet:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """
        The name of the packet. When using XTCE extraction this is the
        fully-qualified name of the first container in the hierarchy that
        this packet maps to.
        """
        return self._proto.id.name

    @property
    def generation_time(self) -> datetime:
        """
        The time when the packet was generated (packet time).
        """
        return parse_server_time(self._proto.generationTime)

    @property
    def earth_reception_time(self) -> Optional[datetime]:
        """
        When the signal was received on the ground.

        .. versionadded:: 1.9.1
        """
        if self._proto.HasField("earthReceptionTime"):
            return parse_server_time(self._proto.earthReceptionTime)
        return None

    @property
    def reception_time(self) -> datetime:
        """
        The time when the packet was received by Yamcs.
        """
        return parse_server_time(self._proto.receptionTime)

    @property
    def sequence_number(self) -> int:
        """
        The sequence number of the packet. This is usually decoded from
        the packet.
        """
        return self._proto.sequenceNumber

    @property
    def link(self) -> str:
        """
        Name of the Yamcs link where this packet was received from.

        .. versionadded:: 1.9.1
        """
        return self._proto.link

    @property
    def binary(self) -> bytes:
        """
        Raw binary of this packet
        """
        if self._proto.HasField("packet"):
            return self._proto.packet
        return b""

    @property
    def size(self) -> int:
        """
        Size in bytes of this packet
        """
        if self._proto.HasField("size"):
            return self._proto.size
        return len(self.binary)

    def __str__(self):
        return f"{self.generation_time} #{self.sequence_number} ({self.name})"


class AlarmRangeSet:
    """
    A set of alarm ranges that apply in a specific context.
    """

    def __init__(
        self,
        context: str,
        watch: Optional[Tuple[Optional[float], Optional[float]]] = None,
        warning: Optional[Tuple[Optional[float], Optional[float]]] = None,
        distress: Optional[Tuple[Optional[float], Optional[float]]] = None,
        critical: Optional[Tuple[Optional[float], Optional[float]]] = None,
        severe: Optional[Tuple[Optional[float], Optional[float]]] = None,
        min_violations: int = 1,
    ):
        """
        :param context:
            Condition under which this range set is
            applicable. The value ``None`` indicates the
            default range set which is only applicable if
            no contextual sets match.
        :param watch:
            Range expressed as a tuple ``(lo, hi)``
            where lo and hi are assumed exclusive.
        :param warning:
            Range expressed as a tuple ``(lo, hi)``
            where lo and hi are assumed exclusive.
        :param distress:
            Range expressed as a tuple ``(lo, hi)``
            where lo and hi are assumed exclusive.
        :param critical:
            Range expressed as a tuple ``(lo, hi)``
            where lo and hi are assumed exclusive.
        :param severe:
            Range expressed as a tuple ``(lo, hi)``
            where lo and hi are assumed exclusive.
        :param min_violations:
            Minimum violations before an alarm is
            generated.
        """
        self.context = context
        self.watch = watch
        self.warning = warning
        self.distress = distress
        self.critical = critical
        self.severe = severe
        self.min_violations = min_violations


class ValueUpdate:
    """
    Data holder for passing a value along with its generation time when
    updating a software parameter.
    """

    def __init__(
        self,
        value: Any,
        generation_time: Optional[datetime] = None,
        expires_in: Optional[float] = None,
    ):
        """
        :param value:
            The value to set
        :param generation_time:
            Generation time of the value. If unset, Yamcs will
            assign the generation time.
        :param expires_in:
            How long before this value expires (in fractional seconds).
            If unset, the value does not expire.

            .. versionadded:: 1.9.1
               Compatible with Yamcs 5.8.8 onwards
        """
        self.value = value
        self.generation_time = generation_time
        self.expires_in = expires_in
