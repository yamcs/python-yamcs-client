import threading
from collections import OrderedDict
from datetime import timedelta

from yamcs.core.exceptions import TimeoutError, YamcsError
from yamcs.core.helpers import parse_server_time, parse_value
from yamcs.model import Event
from yamcs.protobuf.alarms import alarms_pb2
from yamcs.protobuf.pvalue import pvalue_pb2


def _parse_alarm(proto):
    """Converts a protobuf alarm to a specific Alarm implementation."""
    if proto.type == alarms_pb2.PARAMETER:
        return ParameterAlarm(proto)
    if proto.type == alarms_pb2.EVENT:
        return EventAlarm(proto)
    raise YamcsError("Unexpected type " + proto.type)


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

        self.generation_time = parse_server_time(proto.generationTime)
        """
        The generation time as set by Yamcs

        :type: :class:`~datetime.datetime`
        """

        self._proto = proto
        self.attributes = OrderedDict()
        self._update(proto.attr)

    @property
    def name(self):
        """Name of the command."""
        return self._proto.commandName

    @property
    def origin(self):
        """
        The origin of this command. This is often empty, but may
        also be a hostname.
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
    def username(self):
        """Username of the issuer."""
        return self.attributes.get("username")

    @property
    def source(self):
        """String representation of the command."""
        return self.attributes.get("source")

    @property
    def binary(self):
        """Binary representation of the command."""
        return self.attributes.get("binary")

    def is_complete(self):
        """
        Returns whether this command is complete. A command
        can be completed, yet still failed.
        """
        ack = self._assemble_ack("CommandComplete")
        return ack and (ack.status == "OK" or ack.status == "NOK")

    def is_success(self):
        """
        Returns True if the command has completed successfully.
        """
        ack = self._assemble_ack("CommandComplete")
        return ack and ack.status == "OK"

    def is_failure(self):
        """
        Returns True if the command failed.
        """
        ack = self._assemble_ack("CommandComplete")
        return ack and ack.status == "NOK"

    @property
    def error(self):
        """Error message in case the command failed."""
        ack = self._assemble_ack("CommandComplete")
        if ack and ack.status == "NOK":
            return ack.message
        return None

    @property
    def comment(self):
        """Optional user comment attached when issuing the command."""
        return self.attributes.get("comment")

    @property
    def acknowledgments(self):
        """
        All acknowledgments by name.

        :return: Acknowledgments keyed by name.
        :rtype: ~collections.OrderedDict
        """
        acks = OrderedDict()
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

    def _assemble_ack(self, name):
        time = self.attributes.get(name + "_Time")
        status = self.attributes.get(name + "_Status")
        message = self.attributes.get(name + "_Message")
        if time and status:
            return Acknowledgment(name, time, status, message)
        return None

    def _update(self, proto):
        for attr in proto:
            value = parse_value(attr.value)
            self.attributes[attr.name] = value

    def __str__(self):
        acks = ", ".join(ack.__repr__() for _, ack in self.acknowledgments.items())
        return f"{self.name} [{acks}]"


class IssuedCommand:
    def __init__(self, proto):
        self._proto = proto

    @property
    def id(self):
        """
        A unique identifier for this command.
        """
        return self._proto.id

    @property
    def name(self):
        """
        The fully-qualified name of this command.
        """
        if self._proto.HasField("commandName"):
            return self._proto.commandName
        return None

    @property
    def generation_time(self):
        """
        The generation time as set by Yamcs.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("generationTime"):
            return parse_server_time(self._proto.generationTime)
        return None

    @property
    def username(self):
        """The username of the issuer."""
        if self._proto.HasField("username"):
            return self._proto.username
        return None

    @property
    def queue(self):
        """The name of the queue that this command was assigned to."""
        if self._proto.HasField("queue"):
            return self._proto.queue
        return None

    @property
    def origin(self):
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
        if self._proto.HasField("source"):
            return self._proto.source
        return None

    @property
    def hex(self):
        """Hexadecimal string representation of this command."""
        if self._proto.HasField("hex"):
            return self._proto.hex
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

    def disable(self, verifier=None):
        """
        Disable verification.

        :param str verifier: Name of a specific verifier to disable. If unspecified
                             all verifiers are disabled.
        """
        if verifier:
            self._disabled.append(verifier)
        else:
            self._disable_all = True

    def modify_check_window(self, verifier, start=None, stop=None):
        """
        Set or override the check window.

        Depending on the Mission Database configuration,
        the time may be relative to either the command release
        or a preceding verifier.

        :param str verifier: Name of the verifier
        :param float start: Window start time (relative, in seconds)
        :param float stop: Window stop time (relative, in seconds)
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
    def attributes(self):
        if self._cmdhist:
            return self._cmdhist.attributes
        return OrderedDict()

    def is_complete(self):
        """
        Returns whether this command is complete. A command
        can be completed, yet still failed.
        """
        ack = self._assemble_ack("CommandComplete")
        return ack and (ack.status == "OK" or ack.status == "NOK")

    def is_success(self):
        """
        Returns true if this command was completed successfully.
        """
        ack = self._assemble_ack("CommandComplete")
        return ack and ack.status == "OK"

    def await_complete(self, timeout=None):
        """
        Wait for the command to be completed.

        :param float timeout: The amount of seconds to wait.
        """
        self._wait_on_signal(self._completed, timeout)

    def await_acknowledgment(self, name, timeout=None):
        """
        Waits for the result of a specific acknowledgment.

        :param str name: The name of the acknowledgment. Standard names are
                         ``Acknowledge_Queued``, ``Acknowledge_Released``
                         and ``Acknowledge_Sent``. Others depend on
                         specific link types.
        :param float timeout: The amount of seconds to wait.

        :rtype: .Acknowledgment
        """
        event = self._ack_events.setdefault(name, threading.Event())
        self._wait_on_signal(event, timeout)
        return self.acknowledgments.get(name)

    def _wait_on_signal(self, event, timeout=None):
        if not event.wait(timeout=timeout):
            # Remark that a timeout does *not* mean that the underlying
            # work is canceled.
            raise TimeoutError("Timed out.")

    @property
    def error(self):
        """Error message in case the command failed."""
        ack = self._assemble_ack("CommandComplete")
        if ack and ack.status == "NOK":
            return ack.message
        return None

    @property
    def comment(self):
        """Optional user comment attached when issuing the command."""
        return self.attributes.get("comment")

    @property
    def acknowledgments(self):
        """
        All acknowledgments by name.

        :return: Acknowledgments keyed by name.
        :rtype: ~collections.OrderedDict
        """
        acks = OrderedDict()
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

    def _assemble_ack(self, name):
        time = self.attributes.get(name + "_Time")
        status = self.attributes.get(name + "_Status")
        message = self.attributes.get(name + "_Message")
        if time and status:
            return Acknowledgment(name, time, status, message)
        return None

    def _update(self, proto):
        for attr in proto:
            value = parse_value(attr.value)
            self.attributes[attr.name] = value

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
    def update_type(self):
        """Type of update."""
        return alarms_pb2.AlarmNotificationType.Name(self._proto.type)

    @property
    def alarm(self):
        """
        Latest alarm state.

        :type: :class:`.Alarm`
        """
        return _parse_alarm(self._proto)

    def __str__(self):
        return f"[{self.update_type}] {self.alarm}"


class Alarm:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Fully-qualified name of the source of this alarm."""
        if self._proto.id.HasField("namespace"):
            return self._proto.id.namespace + "/" + self._proto.id.name
        return self._proto.id.name

    @property
    def trigger_time(self):
        """
        Processor time when the alarm was triggered.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("triggerTime"):
            return parse_server_time(self._proto.triggerTime)
        return None

    @property
    def severity(self):
        if self._proto.HasField("severity"):
            return alarms_pb2.AlarmSeverity.Name(self._proto.severity)
        return None

    @property
    def sequence_number(self):
        """
        Sequence number for this specific alarm instance. This allows ensuring
        that operations (such as acknowledgment) are done on the expected alarm
        instance.
        """
        if self._proto.HasField("seqNum"):
            return self._proto.seqNum
        return None

    @property
    def is_ok(self):
        """
        True if this alarm is currently 'inactive'.

        For a non-latching alarm this is identical to :meth:`is_process_ok`. A
        latching alarm is only OK if it has returned to normal and was
        acknowledged.
        """
        return not self._proto.triggered

    @property
    def is_process_ok(self):
        """
        True if the process that caused this alarm is OK. For example:
        parameter back within limits.

        For a non-latching alarm this is identical to :meth:`is_ok`.
        """
        return self._proto.processOK

    @property
    def is_latching(self):
        """
        True if this is a latching alarm. A latching alarm returns to
        normal only when the operator resets it
        """
        return self._proto.HasField("latching") and self._proto.latching

    @property
    def is_latched(self):
        """
        True if this alarm is currently latched.
        """
        return self.is_latching and self.is_process_ok and not self.is_ok

    @property
    def is_acknowledged(self):
        """True if this alarm has been acknowledged."""
        return self._proto.acknowledged

    @property
    def acknowledged_by(self):
        """Username of the acknowledger."""
        if self.is_acknowledged and self._proto.acknowledgeInfo.HasField(
            "acknowledgedBy"
        ):
            return self._proto.acknowledgeInfo.acknowledgedBy
        return None

    @property
    def acknowledge_message(self):
        """Comment provided when acknowledging the alarm."""
        if self.is_acknowledged and self._proto.acknowledgeInfo.HasField(
            "acknowledgeMessage"
        ):
            return self._proto.acknowledgeInfo.acknowledgeMessage
        return None

    @property
    def acknowledge_time(self):
        """
        Processor time when the alarm was acknowledged.

        :type: :class:`~datetime.datetime`
        """
        if self.is_acknowledged and self._proto.acknowledgeInfo.HasField(
            "acknowledgeTime"
        ):
            return parse_server_time(self._proto.acknowledgeInfo.acknowledgeTime)
        return None

    @property
    def is_shelved(self):
        """True if this alarm has been shelved."""
        return self._proto.HasField("shelveInfo")

    @property
    def violation_count(self):
        """
        Number of violating samples while this alarm is active.
        """
        if self._proto.HasField("violations"):
            return self._proto.violations
        return None

    @property
    def count(self):
        """
        Total number of samples while this alarm is active.
        """
        if self._proto.HasField("count"):
            return self._proto.count
        return None

    def __str__(self):
        return f"{self.name} ({self.violation_count} violations)"


class ParameterAlarm(Alarm):
    """
    An alarm triggered by a parameter that went out of limits.
    """

    @property
    def trigger_value(self):
        """
        Parameter value that originally triggered the alarm

        :type: :class:`.ParameterValue`
        """
        if self._proto.parameterDetail.HasField("triggerValue"):
            return ParameterValue(self._proto.parameterDetail.triggerValue)
        return None

    @property
    def most_severe_value(self):
        """
        First parameter value that invoked the highest severity
        level of this alarm.

        :type: :class:`.ParameterValue`
        """
        if self._proto.parameterDetail.HasField("mostSevereValue"):
            return ParameterValue(self._proto.parameterDetail.mostSevereValue)
        return None

    @property
    def current_value(self):
        """
        Latest parameter value for this alarm.

        :type: :class:`.ParameterValue`
        """
        if self._proto.parameterDetail.HasField("currentValue"):
            return ParameterValue(self._proto.parameterDetail.currentValue)
        return None


class EventAlarm(Alarm):
    """
    An alarm triggered by an event.
    """

    @property
    def trigger_event(self):
        """
        Event that originally triggered the alarm

        :type: :class:`.Event`
        """
        if self._proto.eventDetail.HasField("triggerEvent"):
            return Event(self._proto.eventDetail.triggerEvent)
        return None

    @property
    def most_severe_event(self):
        """
        First event that invoked the highest severity level
        of this alarm

        :type: :class:`.Event`
        """
        if self._proto.eventDetail.HasField("mostSevereEvent"):
            return Event(self._proto.eventDetail.mostSevereEvent)
        return None

    @property
    def current_event(self):
        """
        Latest event for this alarm

        :type: :class:`.Event`
        """
        if self._proto.eventDetail.HasField("currentEvent"):
            return Event(self._proto.eventDetail.currentEvent)
        return None


class ParameterData:
    def __init__(self, proto, mapping):
        self._proto = proto
        self._mapping = mapping

    @property
    def parameters(self):
        """
        :type: List[:class:`.ParameterValue`]
        """
        pvals = []
        for pval_pb in self._proto.values:
            id = self._mapping[pval_pb.numericId]
            pvals.append(ParameterValue(pval_pb, id=id))
        return pvals


class ParameterValue:
    def __init__(self, proto, id=None):
        self._proto = proto
        self._id = id or proto.id

    @property
    def name(self):
        """
        An identifying name for the parameter value. Typically this is the
        fully-qualified XTCE name, but it may also be an alias depending
        on how the parameter update was requested.
        """
        if self._id.namespace:
            return self._id.namespace + "/" + self._id.name
        return self._id.name

    @property
    def generation_time(self):
        """
        The time when the parameter was generated. If the parameter
        was extracted from a packet, this usually returns the packet time.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("generationTime"):
            return parse_server_time(self._proto.generationTime)
        return None

    @property
    def reception_time(self):
        """
        The time when the parameter value was received by Yamcs.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("acquisitionTime"):
            return parse_server_time(self._proto.acquisitionTime)
        return None

    @property
    def validity_duration(self):
        """
        How long this parameter value is valid.

        .. note: There is also an option when subscribing to get updated when
                 the parameter values expire.

        :type: :class:`~datetime.timedelta`
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
    def monitoring_result(self):
        if self._proto.HasField("monitoringResult"):
            return pvalue_pb2.MonitoringResult.Name(self._proto.monitoringResult)
        return None

    @property
    def range_condition(self):
        """
        If the value is out of limits, this indicates ``LOW`` or ``HIGH``.
        """
        if self._proto.HasField("rangeCondition"):
            return pvalue_pb2.RangeCondition.Name(self._proto.rangeCondition)
        return None

    @property
    def validity_status(self):
        if self._proto.HasField("acquisitionStatus"):
            return pvalue_pb2.AcquisitionStatus.Name(self._proto.acquisitionStatus)
        return None

    @property
    def processing_status(self):
        return self._proto.processingStatus

    def __str__(self):
        line = f"{self.generation_time} {self.name} {self.raw_value} {self.eng_value}"
        if self.monitoring_result:
            line += " [" + self.monitoring_result + "]"
        return line


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

    def __init__(self, context, type, data):
        """
        :param str context: Condition under which this calibrator may be
                            applied. The value ``None`` indicates the
                            default calibrator which is only applied if
                            no contextual calibrators match.
        :param str type: One of ``polynomial`` or ``spline``.
        :param data: Calibration definition for the selected type.
        """
        self.context = context
        self.type = type
        self.data = data


class ContainerData:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """
        The name of the container.
        """
        if self._proto.HasField("name"):
            return self._proto.name
        return None

    @property
    def generation_time(self):
        """
        The time when this container's packet was generated (packet time).

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("generationTime"):
            return parse_server_time(self._proto.generationTime)
        return None

    @property
    def reception_time(self):
        """
        The time when this container's packet was received by Yamcs.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("receptionTime"):
            return parse_server_time(self._proto.receptionTime)
        return None

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
    def name(self):
        """
        The name of the packet. When using XTCE extraction this is the
        fully-qualified name of the first container in the hierarchy that
        this packet maps to.
        """
        if self._proto.HasField("id"):
            return self._proto.id.name
        return None

    @property
    def generation_time(self):
        """
        The time when the packet was generated (packet time).

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("generationTime"):
            return parse_server_time(self._proto.generationTime)
        return None

    @property
    def reception_time(self):
        """
        The time when the packet was received by Yamcs.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("receptionTime"):
            return parse_server_time(self._proto.receptionTime)
        return None

    @property
    def sequence_number(self):
        """
        The sequence number of the packet. This is usually decoded from
        the packet.
        """
        if self._proto.HasField("sequenceNumber"):
            return self._proto.sequenceNumber
        return None

    @property
    def binary(self):
        """
        Raw binary of this packet
        """
        if self._proto.HasField("packet"):
            return self._proto.packet
        return None

    def __str__(self):
        return f"{self.generation_time} #{self.sequence_number} ({self.name})"


class RangeSet:
    """
    A set of alarm range that apply in a specific context.
    """

    def __init__(
        self,
        context,
        watch=None,
        warning=None,
        distress=None,
        critical=None,
        severe=None,
        min_violations=1,
    ):
        """
        :param str context: Condition under which this range set is
                            applicable. The value ``None`` indicates the
                            default range set which is only applicable if
                            no contextual sets match.
        :param (float,float) watch: Range expressed as a tuple ``(lo, hi)``
                                where lo and hi are assumed exclusive.
        :param (float,float) warning: Range expressed as a tuple ``(lo, hi)``
                                  where lo and hi are assumed exclusive.
        :param (float,float) distress: Range expressed as a tuple ``(lo, hi)``
                                   where lo and hi are assumed exclusive.
        :param (float,float) critical: Range expressed as a tuple ``(lo, hi)``
                                   where lo and hi are assumed exclusive.
        :param (float,float) severe: Range expressed as a tuple ``(lo, hi)``
                                 where lo and hi are assumed exclusive.
        :param int min_violations: Minimum violations before an alarm is
                                   generated.
        """
        self.context = context
        self.watch = watch
        self.warning = warning
        self.distress = distress
        self.critical = critical
        self.severe = severe
        self.min_violations = min_violations
