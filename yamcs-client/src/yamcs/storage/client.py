from yamcs.protobuf.buckets import buckets_pb2
from yamcs.storage.model import Bucket, ObjectListing


class StorageClient:
    """
    Client for working with buckets and objects managed by Yamcs.
    """

    def __init__(self, ctx, instance="_global"):
        super(StorageClient, self).__init__()
        self.ctx = ctx
        self._instance = instance

    def list_buckets(self):
        """
        List the buckets.

        :rtype: ~collections.abc.Iterable[.Bucket]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(path="/buckets/" + self._instance)
        message = buckets_pb2.ListBucketsResponse()
        message.ParseFromString(response.content)
        buckets = getattr(message, "buckets")
        return iter([Bucket(bucket, self) for bucket in buckets])

    def get_bucket(self, name):
        """
        Get a specific bucket.

        :param str name: The bucket name.
        :rtype: .Bucket
        """
        # TODO should have an actual server-side operation for this
        for bucket in self.list_buckets():
            if bucket.name == name:
                return bucket
        return None

    def list_objects(self, bucket_name, prefix=None, delimiter=None):
        """
        List the objects for a bucket.

        :param str bucket_name: The name of the bucket.
        :param str prefix: If specified, only objects that start with this
                           prefix are listed.
        :param str delimiter: If specified, return only objects whose name
                              do not contain the delimiter after the prefix.
                              For the other objects, the response contains
                              (in the prefix response parameter) the name
                              truncated after the delimiter. Duplicates are
                              omitted.
        """
        url = f"/buckets/{self._instance}/{bucket_name}/objects"
        params = {}
        if prefix is not None:
            params["prefix"] = prefix
        if delimiter is not None:
            params["delimiter"] = delimiter
        response = self.ctx.get_proto(path=url, params=params)
        message = buckets_pb2.ListObjectsResponse()
        message.ParseFromString(response.content)
        return ObjectListing(message, bucket_name, self)

    def create_bucket(self, bucket_name):
        """
        Create a new bucket.

        :param str bucket_name: The name of the bucket.
        """
        req = buckets_pb2.CreateBucketRequest()
        req.name = bucket_name
        url = f"/buckets/{self._instance}"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def remove_bucket(self, bucket_name):
        """
        Remove a bucket.

        :param str bucket_name: The name of the bucket.
        """
        url = f"/buckets/{self._instance}/{bucket_name}"
        self.ctx.delete_proto(url)

    def download_object(self, bucket_name, object_name):
        """
        Download an object.

        :param str bucket_name: The name of the bucket.
        :param str object_name: The object to fetch.
        """
        url = f"/buckets/{self._instance}/{bucket_name}/objects/{object_name}"
        response = self.ctx.get_proto(path=url)
        return response.content

    def upload_object(self, bucket_name, object_name, file_obj, content_type=None):
        """
        Upload an object to a bucket.

        :param str bucket_name: The name of the bucket.
        :param str object_name: The target name of the object.
        :param file file_obj: The file (or file-like object) to upload.
        :param str content_type: The content type associated to this object.
                                 This is mainly useful when accessing an object
                                 directly via a web browser. If unspecified, a
                                 content type *may* be automatically derived
                                 from the specified ``file_obj``.
        """
        url = f"/buckets/{self._instance}/{bucket_name}/objects/{object_name}"
        if content_type:
            files = {object_name: (object_name, file_obj, content_type)}
        else:
            files = {object_name: (object_name, file_obj)}
        self.ctx.request(path=url, method="post", files=files)

    def remove_object(self, bucket_name, object_name):
        """
        Remove an object from a bucket.

        :param str bucket_name: The name of the bucket.
        :param str object_name: The object to remove.
        """
        url = f"/buckets/{self._instance}/{bucket_name}/objects/{object_name}"
        self.ctx.delete_proto(url)
