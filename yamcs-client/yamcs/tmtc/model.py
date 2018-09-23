from datetime import timedelta

from yamcs.core.helpers import parse_isostring, parse_value
from yamcs.protobuf.alarms import alarms_pb2
from yamcs.protobuf.pvalue import pvalue_pb2


class CommandHistoryEvent(object):

    def __init__(self, name, time, status):
        self.name = name
        """Name of this event."""

        self.time = time
        """Time associated with this event."""

        self.status = status
        """Status associated with this event."""

    def __repr__(self):
        return '{}: {} at {}'.format(self.name, self.status, self.time)

    def __str__(self):
        return self.__repr__()


class CommandHistory(object):

    # TODO Getter for 'ccsds-seqcount' required?

    def __init__(self):
        self.attributes = {}

    @property
    def name(self):
        """Name of the command."""
        return self.attributes.get('cmdName')

    @property
    def username(self):
        """Username of the issuer."""
        return self.attributes.get('username')

    @property
    def source(self):
        """String representation of the command."""
        return self.attributes.get('source')

    @property
    def binary(self):
        """Binary representation of the command."""
        return self.attributes.get('binary')

    @property
    def comment(self):
        """Optional user comment attached when issuing the command."""
        return self.attributes.get('Comment')

    @property
    def transmission_constraints(self):
        return self.attributes.get('TransmissionContraints')

    @property
    def acknowledge_event(self):
        """
        Event indicating the command was acknowledged.

        :type: :class:`.CommandHistoryEvent`
        """
        return self._assemble_event('Acknowledge_Sent')

    @property
    def verification_events(self):
        """
        Events related to command verification.

        :type: List[:class:`.CommandHistoryEvent`]
        """
        queued = self._assemble_event('Verifier_Queued')
        started = self._assemble_event('Verifier_Started')
        return [x for x in [queued, started] if x]

    @property
    def events(self):
        """
        All events.

        :type: List[:class:`.CommandHistoryEvent`]
        """
        events = [self.acknowledge_event] + self.verification_events
        return [x for x in events if x]

    def _assemble_event(self, name):
        time = self.attributes.get(name + '_Time')
        status = self.attributes.get(name + '_Status')
        if time and status:
            return CommandHistoryEvent(name, time, status)
        return None

    def _update(self, proto):
        for attr in proto:
            value = parse_value(attr.value)
            self.attributes[attr.name] = value

    def __str__(self):
        return self.name + str(self.events)


class IssuedCommand(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """
        The fully-qualified name of this command.
        """
        entry = self._proto.commandQueueEntry
        return entry.cmdId.commandName

    @property
    def generation_time(self):
        """
        The generation time as set by Yamcs.

        :rtype: ~datetime.datetime
        """
        entry = self._proto.commandQueueEntry
        if entry.HasField('generationTimeUTC'):
            return parse_isostring(entry.generationTimeUTC)
        return None

    @property
    def username(self):
        """The username of the issuer."""
        entry = self._proto.commandQueueEntry
        if entry.HasField('username'):
            return entry.username
        return None

    @property
    def queue(self):
        """The name of the queue that this command was assigned to."""
        entry = self._proto.commandQueueEntry
        if entry.HasField('queueName'):
            return entry.queueName
        return None

    @property
    def origin(self):
        """
        The origin of this command. This is often empty, but may
        also be a hostname.
        """
        entry = self._proto.commandQueueEntry
        if entry.cmdId.HasField('origin'):
            return parse_isostring(entry.cmdId.origin)
        return None

    @property
    def sequence_number(self):
        """
        The sequence number of this command. This is the sequence
        number assigned by the issuing client.
        """
        entry = self._proto.commandQueueEntry
        if entry.cmdId.HasField('sequenceNumber'):
            return entry.cmdId.sequenceNumber
        return None

    @property
    def source(self):
        """String representation of this command."""
        if self._proto.HasField('source'):
            return self._proto.source
        return None

    @property
    def hex(self):
        """Hexadecimal string representation of this command."""
        if self._proto.HasField('hex'):
            return self._proto.hex
        return None

    @property
    def binary(self):
        """Binary representation of this command."""
        if self._proto.HasField('binary'):
            return self._proto.binary
        return None

    def __str__(self):
        return '{} {}'.format(self.generation_time, self.source)


class AlarmEvent(object):
    """
    Object received through callbacks when subscribing to alarm updates.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def event_type(self):
        """Type of update."""
        return alarms_pb2.AlarmData.Type.Name(self._proto.type)

    @property
    def alarm(self):
        """
        Latest alarm state.

        :type: :class:`.Alarm`
        """
        return Alarm(self._proto)

    def __str__(self):
        return '[{}] {}'.format(self.event_type, self.alarm)


class Alarm(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Fully-qualified XTCE name of the parameter that triggered this alarm."""
        return self.trigger_value.name

    @property
    def sequence_number(self):
        """
        Sequence number for this specific alarm instance. This allows ensuring
        that operations (such as acknowledgment) are done on the expected alarm
        instance.
        """
        if self._proto.HasField('seqNum'):
            return self._proto.seqNum
        return None

    @property
    def is_acknowledged(self):
        """Whether this alarm has been acknowledged."""
        return self._proto.HasField('acknowledgeInfo')

    @property
    def acknowledged_by(self):
        """Username of the acknowledger."""
        if (self.is_acknowledged and
                self._proto.acknowledgeInfo.HasField('acknowledgedBy')):
            return self._proto.acknowledgeInfo.acknowledgedBy
        return None

    @property
    def acknowledge_message(self):
        """Comment provided when acknowledging the alarm."""
        if (self.is_acknowledged and
                self._proto.acknowledgeInfo.HasField('acknowledgeMessage')):
            return self._proto.acknowledgeInfo.acknowledgeMessage
        return None

    @property
    def acknowledge_time(self):
        """
        Processor time when the alarm was acknowledged.

        :type: :class:`~datetime.datetime`
        """
        if (self.is_acknowledged and
                self._proto.acknowledgeInfo.HasField('acknowledgeTime')):
            return parse_isostring(self._proto.acknowledgeInfo.acknowledgeTime)
        return None

    @property
    def trigger_value(self):
        """
        Parameter value that originally triggered the alarm

        :type: :class:`.ParameterValue`
        """
        if self._proto.HasField('triggerValue'):
            return ParameterValue(self._proto.triggerValue)
        return None

    @property
    def most_severe_value(self):
        """
        First parameter value that invoked the highest severity
        level of this alarm.

        :type: :class:`.ParameterValue`
        """
        if self._proto.HasField('mostSevereValue'):
            return ParameterValue(self._proto.mostSevereValue)
        return None

    @property
    def current_value(self):
        """
        Latest parameter value for this alarm.

        :type: :class:`.ParameterValue`
        """
        if self._proto.HasField('currentValue'):
            return ParameterValue(self._proto.currentValue)
        return None

    @property
    def violation_count(self):
        """
        Number of parameter updates that violated limits while
        this alarm is active.
        """
        if self._proto.HasField('violations'):
            return self._proto.violations
        return None

    def __str__(self):
        return '{} ({} violations)'.format(
            self.trigger_value, self.violation_count)


class ParameterData(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def parameters(self):
        """
        :type: List[:class:`.ParameterValue`]
        """
        return [ParameterValue(p) for p in self._proto.parameter]


class ParameterValue(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """
        An identifying name for the parameter value. Typically this is the
        fully-qualified XTCE name, but it may also be an alias depending
        on how the parameter update was requested.
        """
        if self._proto.id.namespace:
            return self._proto.id.namespace + '/' + self._proto.id.name
        return self._proto.id.name

    @property
    def generation_time(self):
        """
        The time when the parameter was generated. If the parameter
        was extracted from a packet, this usually returns the packet time.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField('generationTimeUTC'):
            return parse_isostring(self._proto.generationTimeUTC)
        return None

    @property
    def reception_time(self):
        """
        The time when the parameter value was received by Yamcs.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField('acquisitionTimeUTC'):
            return parse_isostring(self._proto.acquisitionTimeUTC)
        return None

    @property
    def validity_duration(self):
        """
        How long this parameter value is valid.

        .. note: There is also an option when subscribing to get updated when
                 the parameter values expire.

        :type: :class:`~datetime.timedelta`
        """
        if self._proto.HasField('expireMillis'):
            return timedelta(milliseconds=self._proto.expireMillis)
        return None

    @property
    def raw_value(self):
        """
        The raw (uncalibrated) value.
        """
        if self._proto.HasField('rawValue'):
            return parse_value(self._proto.rawValue)
        return None

    @property
    def eng_value(self):
        """
        The engineering (calibrated) value.
        """
        if self._proto.HasField('engValue'):
            return parse_value(self._proto.engValue)
        return None

    @property
    def monitoring_result(self):
        if self._proto.HasField('monitoringResult'):
            return pvalue_pb2.MonitoringResult.Name(self._proto.monitoringResult)
        return None

    @property
    def range_condition(self):
        """
        If the value is out of limits, this indicates ``LOW`` or ``HIGH``.
        """
        if self._proto.HasField('rangeCondition'):
            return pvalue_pb2.RangeCondition.Name(self._proto.rangeCondition)
        return None

    @property
    def validity_status(self):
        if self._proto.HasField('acquisitionStatus'):
            return pvalue_pb2.AcquisitionStatus.Name(self._proto.acquisitionStatus)
        return None

    @property
    def processing_status(self):
        return self._proto.processingStatus

    def __str__(self):
        line = '{} {} {}'.format(self.generation_time, self.name, self.eng_value)
        if self.monitoring_result:
            line += ' [' + self.monitoring_result + ']'
        return line
