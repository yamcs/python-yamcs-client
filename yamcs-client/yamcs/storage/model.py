from yamcs.core.helpers import parse_isostring


class Bucket(object):

    def __init__(self, proto, instance, client):
        self._proto = proto
        self._instance = instance
        self._client = client

    @property
    def name(self):
        """Name of this bucket."""
        return self._proto.name

    @property
    def object_count(self):
        """Number of objects in this bucket."""
        return self._proto.numObjects

    @property
    def size(self):
        """Total size in bytes of this bucket (excluding metadata)."""
        return self._proto.size

    def list_objects(self):
        return self._client.list_objects(
            instance=self._instance, bucket_name=self.name)

    def __str__(self):
        return self.name


class ObjectListing(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def prefixes(self):
        return [p for p in self._proto.prefix]

    @property
    def objects(self):
        return [ObjectInfo(o) for o in self._proto.object]


class ObjectInfo(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        return self._proto.name

    @property
    def size(self):
        """Size in bytes of this object (excluding metadata)."""
        return self._proto.size

    @property
    def created(self):
        if self._proto.HasField('created'):
            return parse_isostring(self._proto.created)
        return None

    def __str__(self):
        return '{} ({} bytes, created {})'.format(
            self.name, self.size, self.created)
