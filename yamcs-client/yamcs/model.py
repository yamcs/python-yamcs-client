from yamcs.core.helpers import parse_isostring
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.yamcsManagement import yamcsManagement_pb2


class Event(object):
    """
    A timetagged free-text message. Events work a lot like log
    messages in logging frameworks, but then targeted at operators.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def generation_time(self):
        """
        The time when the event was generated.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField('generationTimeUTC'):
            return parse_isostring(self._proto.generationTimeUTC)
        return None

    @property
    def reception_time(self):
        """
        The time when the event was received by Yamcs.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField('receptionTimeUTC'):
            return parse_isostring(self._proto.receptionTimeUTC)
        return None

    @property
    def severity(self):
        """
        Severity level of the event. One of ``INFO``, ``WATCH``,
        ``WARNING``, ``DISTRESS``, ``CRITICAL`` or ``SEVERE``.
        """
        if self._proto.HasField('severity'):
            return yamcs_pb2.Event.EventSeverity.Name(self._proto.severity)
        return None

    @property
    def message(self):
        """
        Event message.
        """
        if self._proto.HasField('message'):
            return self._proto.message
        return None

    @property
    def sequence_number(self):
        """
        Sequence number. Usually this is assigned by the source of the event.
        """
        if self._proto.HasField('seqNumber'):
            return self._proto.seqNumber
        return None

    @property
    def event_type(self):
        """
        The event type. This is mission-specific and can be any string.
        """
        if self._proto.HasField('type'):
            return self._proto.type
        return None

    @property
    def source(self):
        """
        The event source. Can be any string.
        """
        if self._proto.HasField('source'):
            return self._proto.source
        return None

    def __str__(self):
        return '{} [{}] {}'.format(self.generation_time, self.severity, self.message)


class LinkEvent(object):
    """
    Data holder used in link subscriptions.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def event_type(self):
        """
        The type of the event. One of ``REGISTERED``, ``UNREGISTERED``,
        or ``UPDATED``.
        """
        return yamcsManagement_pb2.LinkEvent.Type.Name(self._proto.type)

    @property
    def link(self):
        """
        Link state at the time of this event.

        :type: :class:`.Link`
        """
        return Link(self._proto.linkInfo)

    def __str__(self):
        return '[{}] {}'.format(self.event_type, self.link)

class Link(object):
    """
    Represents a link with an external system. Depending on the
    semantics of the link, this may imply inbound data, outbound
    data or a combination of both.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def instance(self):
        """Name of the instance where this link is defined."""
        return self._proto.instance

    @property
    def name(self):
        """Name of this link (unique per instance)."""
        return self._proto.name

    @property
    def enabled(self):
        """If ``True``, this link accepts or outputs data."""
        return not self._proto.disabled

    @property
    def status(self):
        """Short status."""
        return self._proto.status

    @property
    def in_count(self):
        """The number of inbound data events (example: packet count)."""
        return self._proto.dataInCount

    @property
    def out_count(self):
        """The number of outbound data events (example: command count)."""
        return self._proto.dataOutCount

    def __str__(self):
        return '{}/{}: {} (in: {} out: {})'.format(
            self.instance, self.name, self.status, self.in_count, self.out_count)
