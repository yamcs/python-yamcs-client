from yamcs.core.helpers import parse_isostring


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
