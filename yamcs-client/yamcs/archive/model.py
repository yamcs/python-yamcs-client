from yamcs.core.helpers import parse_isostring


class IndexChunk(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        if self._proto.HasField('id'):
            return self._proto.id.name
        return None

    @property
    def records(self):
        return [IndexRecord(rec) for rec in self._proto.entry]

    def __str__(self):
        return '{} ({} records)'.format(self.name, len(self.records))


class IndexRecord(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def start(self):
        return parse_isostring(self._proto.start)

    @property
    def stop(self):
        return parse_isostring(self._proto.stop)

    @property
    def count(self):
        return self._proto.count

    def __str__(self):
        return '{} - {} (n={})'.format(self.start, self.stop, self.count)
