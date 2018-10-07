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

    def download_object(self, object_name):
        return self._client.download_object(
            self._instance, self.name, object_name)

    def upload_object(self, object_name, file_obj):
        return self._client.upload_object(
            self._instance, self.name, object_name, file_obj)

    def delete_object(self, object_name):
        self._client.remove_object(self._instance, self.name, object_name)

    def delete(self):
        self._client.remove_bucket(self._instance, self.name)

    def __str__(self):
        return self.name


class ObjectListing(object):

    def __init__(self, proto, instance, bucket, client):
        self._proto = proto
        self._instance = instance
        self._bucket = bucket
        self._client = client

    @property
    def prefixes(self):
        return [p for p in self._proto.prefix]

    @property
    def objects(self):
        return [ObjectInfo(o, self._instance, self._bucket, self._client)
                for o in self._proto.object]


class ObjectInfo(object):

    def __init__(self, proto, instance, bucket, client):
        self._proto = proto
        self._instance = instance
        self._bucket = bucket
        self._client = client

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

    def delete(self):
        self._client.remove_object(self._instance, self._bucket, self.name)

    def download(self):
        return self._client.download_object(
            self._instance, self._bucket, self.name)

    def upload(self, file_obj):
        return self._client.upload_object(
            self._instance, self._bucket, self.name, file_obj)

    def __str__(self):
        return '{} ({} bytes, created {})'.format(
            self.name, self.size, self.created)
