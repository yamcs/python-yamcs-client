from yamcs.core.helpers import parse_isostring
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.yamcsManagement import yamcsManagement_pb2


class Event(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def generation_time(self):
        if self._proto.HasField('generationTimeUTC'):
            return parse_isostring(self._proto.generationTimeUTC)
        return None

    @property
    def reception_time(self):
        if self._proto.HasField('receptionTimeUTC'):
            return parse_isostring(self._proto.receptionTimeUTC)
        return None

    @property
    def severity(self):
        if self._proto.HasField('severity'):
            return yamcs_pb2.Event.EventSeverity.Name(self._proto.severity)
        return None

    @property
    def message(self):
        if self._proto.HasField('message'):
            return self._proto.message
        return None

    @property
    def sequence_number(self):
        if self._proto.HasField('seqNumber'):
            return self._proto.seqNumber
        return None

    @property
    def event_type(self):
        if self._proto.HasField('type'):
            return self._proto.type
        return None

    @property
    def source(self):
        if self._proto.HasField('source'):
            return self._proto.source
        return None

    def __str__(self):
        return '{} [{}] {}'.format(self.generation_time, self.severity, self.message)


class LinkEvent(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def event_type(self):
        return yamcsManagement_pb2.LinkEvent.Type.Name(self._proto.type)

    @property
    def link(self):
        """
        :type: :class:`.Link`
        """
        return Link(self._proto.linkInfo)

    def __str__(self):
        return '[{}] {}'.format(self.event_type, self.link)

class Link(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def instance(self):
        return self._proto.instance

    @property
    def name(self):
        return self._proto.name

    @property
    def enabled(self):
        return not self._proto.disabled

    @property
    def status(self):
        return self._proto.status

    @property
    def in_count(self):
        return self._proto.dataInCount

    @property
    def out_count(self):
        return self._proto.dataOutCount

    def __str__(self):
        return '{}/{}: {} (in: {} out: {})'.format(
            self.instance, self.name, self.status, self.in_count, self.out_count)
