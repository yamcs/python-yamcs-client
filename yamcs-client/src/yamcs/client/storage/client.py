from typing import IO, Any, Iterable, Mapping, Optional, Union

from yamcs.client.core.context import Context
from yamcs.client.core.exceptions import NotFound
from yamcs.client.storage.model import Bucket, ObjectListing
from yamcs.protobuf.buckets import buckets_pb2

__all__ = [
    "StorageClient",
]


class StorageClient:
    """
    Client for working with buckets and objects managed by Yamcs.
    """

    def __init__(self, ctx: Context):
        super(StorageClient, self).__init__()
        self.ctx = ctx

    def list_buckets(self) -> Iterable[Bucket]:
        """
        List the buckets.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(path="/storage/buckets")
        message = buckets_pb2.ListBucketsResponse()
        message.ParseFromString(response.content)
        buckets = getattr(message, "buckets")
        return iter([Bucket(bucket, self) for bucket in buckets])

    def get_bucket(self, name: str, create=False) -> Bucket:
        """
        Get a specific bucket.

        :param name:
            The bucket name.
        :param create:
            If specified, create the bucket if it does not yet exist.
        """
        url = "/storage/buckets/" + name

        if create:
            try:
                response = self.ctx.get_proto(path=url)
            except NotFound:
                self.create_bucket(name)
                response = self.ctx.get_proto(path=url)
        else:
            response = self.ctx.get_proto(path=url)
        message = buckets_pb2.BucketInfo()
        message.ParseFromString(response.content)
        return Bucket(message, self)

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
        url = f"/storage/buckets/{bucket_name}/objects"
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
        url = "/storage/buckets"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def remove_bucket(self, bucket_name: str):
        """
        Remove a bucket.

        :param bucket_name:
            The name of the bucket.
        """
        url = f"/storage/buckets/{bucket_name}"
        self.ctx.delete_proto(url)

    def download_object(self, bucket_name: str, object_name: str) -> bytes:
        """
        Download an object.

        :param bucket_name:
            The name of the bucket.
        :param object_name:
            The object to fetch.
        """
        url = f"/storage/buckets/{bucket_name}/objects/{object_name}"
        response = self.ctx.get_proto(path=url)
        return response.content

    def upload_object(
        self,
        bucket_name: str,
        object_name: str,
        file_obj: Union[str, IO],
        content_type: Optional[str] = None,
        metadata: Optional[Mapping[str, str]] = None,
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
        :param metadata:
            Optional metadata associated to this object.
        """
        url = f"/storage/buckets/{bucket_name}/objects/{object_name}"
        if content_type:
            files: Any = {object_name: (object_name, file_obj, content_type)}
        else:
            files: Any = {object_name: (object_name, file_obj)}
        if metadata:
            for k, v in metadata.items():
                files[k] = (None, v)
        self.ctx.request(path=url, method="post", files=files)

    def remove_object(self, bucket_name: str, object_name: str):
        """
        Remove an object from a bucket.

        :param bucket_name:
            The name of the bucket.
        :param object_name:
            The object to remove.
        """
        url = f"/storage/buckets/{bucket_name}/objects/{object_name}"
        self.ctx.delete_proto(url)
