from typing import IO, Iterable, Optional

from yamcs.core.context import Context
from yamcs.protobuf.buckets import buckets_pb2
from yamcs.storage.model import Bucket, ObjectListing


class StorageClient:
    """
    Client for working with buckets and objects managed by Yamcs.
    """

    def __init__(self, ctx: Context, instance: str = "_global"):
        super(StorageClient, self).__init__()
        self.ctx = ctx
        self._instance = instance

    def list_buckets(self) -> Iterable[Bucket]:
        """
        List the buckets.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(path="/buckets/" + self._instance)
        message = buckets_pb2.ListBucketsResponse()
        message.ParseFromString(response.content)
        buckets = getattr(message, "buckets")
        return iter([Bucket(bucket, self) for bucket in buckets])

    def get_bucket(self, name: str) -> Bucket:
        """
        Get a specific bucket.

        :param name:
            The bucket name.
        """
        # TODO should have an actual server-side operation for this
        # (added in Yamcs 5.6.1)
        for bucket in self.list_buckets():
            if bucket.name == name:
                return bucket
        return None

    def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> ObjectListing:
        """
        List the objects for a bucket.

        :param bucket_name:
            The name of the bucket.
        :param prefix:
            If specified, only objects that start with this
            prefix are listed.
        :param delimiter:
            If specified, return only objects whose name
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

    def create_bucket(self, bucket_name: str):
        """
        Create a new bucket.

        :param bucket_name:
            The name of the bucket.
        """
        req = buckets_pb2.CreateBucketRequest()
        req.name = bucket_name
        url = f"/buckets/{self._instance}"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def remove_bucket(self, bucket_name: str):
        """
        Remove a bucket.

        :param bucket_name:
            The name of the bucket.
        """
        url = f"/buckets/{self._instance}/{bucket_name}"
        self.ctx.delete_proto(url)

    def download_object(self, bucket_name: str, object_name: str):
        """
        Download an object.

        :param bucket_name:
            The name of the bucket.
        :param object_name:
            The object to fetch.
        """
        url = f"/buckets/{self._instance}/{bucket_name}/objects/{object_name}"
        response = self.ctx.get_proto(path=url)
        return response.content

    def upload_object(
        self,
        bucket_name: str,
        object_name: str,
        file_obj: IO,
        content_type: Optional[str] = None,
    ):
        """
        Upload an object to a bucket.

        :param bucket_name:
            The name of the bucket.
        :param object_name:
            The target name of the object.
        :param file_obj:
            The file (or file-like object) to upload.
        :param content_type:
            The content type associated to this object.
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

    def remove_object(self, bucket_name: str, object_name: str):
        """
        Remove an object from a bucket.

        :param bucket_name:
            The name of the bucket.
        :param object_name:
            The object to remove.
        """
        url = f"/buckets/{self._instance}/{bucket_name}/objects/{object_name}"
        self.ctx.delete_proto(url)
