from datetime import timedelta

from yamcs.core.helpers import parse_isostring, parse_value
from yamcs.protobuf.pvalue import pvalue_pb2


class CommandHistoryEvent(object):

    def __init__(self, name, time, status):
        self.name = name
        self.time = time
        self.status = status

    def __repr__(self):
        return '{}: {} at {}'.format(self.name, self.status, self.time)

    def __str__(self):
        return self.__repr__()


class CommandHistoryRecord(object):

    # TODO Getter for 'ccsds-seqcount' required?

    def __init__(self):
        self.attributes = {}

    @property
    def name(self):
        return self.attributes.get('cmdName')

    @property
    def username(self):
        return self.attributes.get('username')

    @property
    def source(self):
        return self.attributes.get('source')

    @property
    def binary(self):
        return self.attributes.get('binary')

    @property
    def comment(self):
        return self.attributes.get('Comment')

    @property
    def transmission_constraints(self):
        return self.attributes.get('TransmissionContraints')

    @property
    def acknowledge_event(self):
        return self._assemble_event('Acknowledge_Sent')

    @property
    def verification_events(self):
        queued = self._assemble_event('Verifier_Queued')
        started = self._assemble_event('Verifier_Started')
        return [x for x in [queued, started] if x]

    @property
    def events(self):
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
        The fully-qualified name of the issued command.
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
        """
        The username of the issuer
        """
        entry = self._proto.commandQueueEntry
        if entry.HasField('username'):
            return entry.username
        return None

    @property
    def queue(self):
        """The name of the queue that the command was assigned to."""
        entry = self._proto.commandQueueEntry
        if entry.HasField('queueName'):
            return entry.queueName
        return None

    @property
    def origin(self):
        """
        The origin of the issued command. This is often empty, but may
        also be a hostname.
        """
        entry = self._proto.commandQueueEntry
        if entry.cmdId.HasField('origin'):
            return parse_isostring(entry.cmdId.origin)
        return None

    @property
    def sequence_number(self):
        """
        The sequence number of the issued command. This is the sequence
        number assigned by the issuing client.
        """
        entry = self._proto.commandQueueEntry
        if entry.cmdId.HasField('sequenceNumber'):
            return entry.cmdId.sequenceNumber
        return None

    @property
    def source(self):
        """
        The source of the command. This may be simply the username,
        or in some cases a string in the fomat ``USER@HOST``.
        """
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


class ParameterData(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def parameters(self):
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
