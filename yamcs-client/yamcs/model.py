from yamcs.protobuf.yamcsManagement import yamcsManagement_pb2


class LinkEvent(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def event_type(self):
        return yamcsManagement_pb2.LinkEvent.Type.Name(self._proto.type)

    @property
    def link(self):
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
