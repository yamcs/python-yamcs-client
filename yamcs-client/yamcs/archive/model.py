from yamcs.core.helpers import parse_isostring, parse_value


class Table(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Table name."""
        return self._proto.name

    def __str__(self):
        return self.name


class Stream(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Stream name."""
        return self._proto.name

    def __str__(self):
        return self.name


class StreamData(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def stream(self):
        """Stream name."""
        return self._proto.stream

    @property
    def columns(self):
        """Tuple columns."""
        return [ColumnData(c) for c in self._proto.column]

    def __str__(self):
        return '{} ({} columns)'.format(self.stream, len(self.columns))


class ColumnData(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Column name."""
        return self._proto.name

    @property
    def value(self):
        """Value for this column."""
        return parse_value(self._proto.value)

    def __str__(self):
        return '{}: {}'.format(self.name, self.value)


class IndexGroup(object):
    """
    Group of index records that represent the same
    type of underlying objects.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """
        Name associated with this group. The meaning is defined
        by the objects represented by this index. For example:

        * In an index of events, index records are grouped by ``source``.
        * In an index of packets, index records are grouped by ``packet name``.
        """
        if self._proto.HasField('id'):
            return self._proto.id.name
        return None

    @property
    def records(self):
        """
        Index records within this group

        :type: List[:class:`.IndexRecord`]
        """
        return [IndexRecord(rec) for rec in self._proto.entry]

    def __str__(self):
        return '{} ({} records)'.format(self.name, len(self.records))


class IndexRecord(object):
    """
    Represents a block of uninterrupted data (derived from the index definition
    for the type of underlying objects, in combination with the requested
    ``merge_time``.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def start(self):
        """
        Start time of the record

        :type: :class:`~datetime.datetime`
        """
        return parse_isostring(self._proto.start)

    @property
    def stop(self):
        """
        Stop time of the record

        :type: :class:`~datetime.datetime`
        """
        return parse_isostring(self._proto.stop)

    @property
    def count(self):
        """
        Number of underlying objects this index record represents
        """
        return self._proto.count

    def __str__(self):
        return '{} - {} (n={})'.format(self.start, self.stop, self.count)


class Packet(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """
        The name of the packet. When using XTCE extraction this is the
        fully-qualified name of the first container in the hierarchy that
        this packet maps to.
        """
        if self._proto.HasField('id'):
            return self._proto.id.name
        return None

    @property
    def generation_time(self):
        """
        The time when the packet was generated (packet time).

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField('generationTimeUTC'):
            return parse_isostring(self._proto.generationTimeUTC)
        return None

    @property
    def reception_time(self):
        """
        The time when the packet was received by Yamcs.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField('receptionTimeUTC'):
            return parse_isostring(self._proto.receptionTimeUTC)
        return None

    @property
    def sequence_number(self):
        """
        The sequence number of the packet. This is usually decoded from
        the packet.
        """
        if self._proto.HasField('sequenceNumber'):
            return self._proto.sequenceNumber
        return None

    @property
    def binary(self):
        """
        Raw binary of this packet
        """
        if self._proto.HasField('packet'):
            return self._proto.packet
        return None

    def __str__(self):
        return '{} #{} ({})'.format(self.generation_time, self.sequence_number, self.name)


class Sample(object):
    """
    Provides aggregation properties over a range of a parameter's
    values.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def time(self):
        """
        Sample time.

        :type: :class:`~datetime.datetime`
        """
        return parse_isostring(self._proto.time)

    @property
    def avg(self):
        """Average value."""
        if self._proto.HasField('avg'):
            return self._proto.avg
        return None

    @property
    def min(self):
        """Minimum value."""
        if self._proto.HasField('min'):
            return self._proto.min
        return None

    @property
    def max(self):
        """Maximum value."""
        if self._proto.HasField('max'):
            return self._proto.max
        return None

    @property
    def parameter_count(self):
        """The number of parameter values this sample represents."""
        return self._proto.n

    def __str__(self):
        return '{} {}'.format(self.time, self.avg)


class ParameterRange(object):
    """
    Indicates an interval during which a parameter's
    value was uninterrupted and unchanged.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def start(self):
        """
        Start time of this range (inclusive).

        :type: :class:`~datetime.datetime`
        """
        return parse_isostring(self._proto.timeStart)

    @property
    def stop(self):
        """
        Stop time of this range (exclusive).
        
        :type: :class:`~datetime.datetime`
        """
        return parse_isostring(self._proto.timeStop)

    @property
    def eng_value(self):
        """The engineering (calibrated) value."""
        return parse_value(self._proto.engValue)

    @property
    def parameter_count(self):
        """The number of received parameter values during this range."""
        return self._proto.count

    def __str__(self):
        return '{} - {}: {}'.format(self.start, self.stop, self.eng_value)
