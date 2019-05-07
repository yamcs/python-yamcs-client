from yamcs.core.client import BaseClient
from yamcs.protobuf.rest import rest_pb2
from yamcs.storage.model import Bucket, ObjectListing


class Client(object):
    """
    Client for working with buckets and objects managed by Yamcs.
    """

    def __init__(self, address, **kwargs):
        """
        :param str address: The address of Yamcs in the format 'hostname:port'
        :param bool tls: Whether TLS encryption is expected
        :param bool tls_verify: Whether server certificate verification is enabled
                                (only applicable if ``tls=True``)
        :param .Credentials credentials: Credentials for when the server is secured
        :param str user_agent: Optionally override the default user agent
        """
        super(Client, self).__init__()
        self._client = BaseClient(address, **kwargs)

    def list_buckets(self, instance):
        """
        List the buckets for an instance.

        :param str instance: A Yamcs instance name.
        :rtype: ~collections.Iterable[.Bucket]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self._client.get_proto(path='/buckets/' + instance)
        message = rest_pb2.ListBucketsResponse()
        message.ParseFromString(response.content)
        buckets = getattr(message, 'bucket')
        return iter([
            Bucket(bucket, instance, self) for bucket in buckets])

    def list_objects(self, instance, bucket_name, prefix=None, delimiter=None):
        """
        List the objects for a bucket.

        :param str instance: A Yamcs instance name.
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
        url = '/buckets/{}/{}'.format(instance, bucket_name)
        params = {}
        if prefix is not None:
            params['prefix'] = prefix
        if delimiter is not None:
            params['delimiter'] = delimiter
        response = self._client.get_proto(path=url, params=params)
        message = rest_pb2.ListObjectsResponse()
        message.ParseFromString(response.content)
        return ObjectListing(message, instance, bucket_name, self)

    def create_bucket(self, instance, bucket_name):
        """
        Create a new bucket in the specified instance.

        :param str instance: A Yamcs instance name.
        :param str bucket_name: The name of the bucket.
        """
        req = rest_pb2.CreateBucketRequest()
        req.name = bucket_name
        url = '/buckets/{}'.format(instance)
        self._client.post_proto(url, data=req.SerializeToString())

    def remove_bucket(self, instance, bucket_name):
        """
        Remove a bucket from the specified instance.

        :param str instance: A Yamcs instance name.
        :param str bucket_name: The name of the bucket.
        """
        url = '/buckets/{}/{}'.format(instance, bucket_name)
        self._client.delete_proto(url)

    def download_object(self, instance, bucket_name, object_name):
        """
        Download an object.

        :param str instance: A Yamcs instance name.
        :param str bucket_name: The name of the bucket.
        :param str object_name: The object to fetch.
        """
        url = '/buckets/{}/{}/{}'.format(instance, bucket_name, object_name)
        response = self._client.get_proto(path=url)
        return response.content

    def upload_object(self, instance, bucket_name, object_name, file_obj,
                      content_type=None):
        """
        Upload an object to a bucket.

        :param str instance: A Yamcs instance name.
        :param str bucket_name: The name of the bucket.
        :param str object_name: The target name of the object.
        :param file file_obj: The file (or file-like object) to upload.
        :param str content_type: The content type associated to this object.
                                 This is mainly useful when accessing an object
                                 directly via a web browser. If unspecified, a
                                 content type *may* be automatically derived
                                 from the specified ``file_obj``.
        """
        url = '/buckets/{}/{}/{}'.format(instance, bucket_name, object_name)
        with open(file_obj, 'rb') as f:
            if content_type:
                files = {object_name: (object_name, f, content_type)}
            else:
                files = {object_name: (object_name, f)}
            self._client.request(path=url, method='post', files=files)

    def remove_object(self, instance, bucket_name, object_name):
        """
        Remove an object from a bucket.

        :param str instance: A Yamcs instance name.
        :param str bucket_name: The name of the bucket.
        :param str object_name: The object to remove.
        """
        url = '/buckets/{}/{}/{}'.format(instance, bucket_name, object_name)
        self._client.delete_proto(url)
