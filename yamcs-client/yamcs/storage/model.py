from yamcs.core.helpers import parse_server_time


class Bucket:
    def __init__(self, proto, storage_client):
        self._proto = proto
        self._storage_client = storage_client

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

    def list_objects(self, prefix=None, delimiter=None):
        """
        List the objects for this bucket.

        :param str prefix: If specified, only objects that start with this
                           prefix are listed.
        :param str delimiter: If specified, return only objects whose name
                              do not contain the delimiter after the prefix.
                              For the other objects, the response contains
                              (in the prefix response parameter) the name
                              truncated after the delimiter. Duplicates are
                              omitted.
        """
        return self._storage_client.list_objects(
            bucket_name=self.name, prefix=prefix, delimiter=delimiter,
        )

    def download_object(self, object_name):
        """
        Download an object.

        :param str object_name: The object to fetch.
        """
        return self._storage_client.download_object(self.name, object_name)

    def upload_object(self, object_name, file_obj, content_type=None):
        """
        Upload an object to this bucket.

        :param str object_name: The target name of the object.
        :param file file_obj: The file (or file-like object) to upload.
        :param str content_type: The content type associated to this object.
                                 This is mainly useful when accessing an object
                                 directly via a web browser. If unspecified, a
                                 content type *may* be automatically derived
                                 from the specified ``file_obj``.
        """
        return self._storage_client.upload_object(
            self.name, object_name, file_obj, content_type=content_type
        )

    def delete_object(self, object_name):
        """
        Remove an object from this bucket.

        :param str object_name: The object to remove.
        """
        self._storage_client.remove_object(self.name, object_name)

    def delete(self):
        """
        Remove this bucket in its entirety.
        """
        self._storage_client.remove_bucket(self.name)

    def __str__(self):
        return self.name


class ObjectListing:
    def __init__(self, proto, bucket, storage_client):
        self._proto = proto
        self._bucket = bucket
        self._storage_client = storage_client

    @property
    def prefixes(self):
        """
        The prefixes in this listing.

        :type: str[]
        """
        return [p for p in self._proto.prefixes]

    @property
    def objects(self):
        """
        The objects in this listing.

        :type: List[:class:`.ObjectInfo`]
        """
        return [
            ObjectInfo(o, self._bucket, self._storage_client)
            for o in self._proto.objects
        ]


class ObjectInfo:
    def __init__(self, proto, bucket, storage_client):
        self._proto = proto
        self._bucket = bucket
        self._storage_client = storage_client

    @property
    def name(self):
        """The name of this object."""
        return self._proto.name

    @property
    def size(self):
        """Size in bytes of this object (excluding metadata)."""
        return self._proto.size

    @property
    def created(self):
        """
        Return when this object was created (or re-created).

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("created"):
            return parse_server_time(self._proto.created)
        return None

    def delete(self):
        """Remove this object."""
        self._storage_client.remove_object(self._bucket, self.name)

    def download(self):
        """Download this object."""
        return self._storage_client.download_object(self._bucket, self.name)

    def upload(self, file_obj):
        """
        Replace the content of this object.

        :param file file_obj: The file (or file-like object) to upload.
        """
        return self._storage_client.upload_object(self._bucket, self.name, file_obj)

    def __str__(self):
        return f"{self.name} ({self.size} bytes, created {self.created})"
