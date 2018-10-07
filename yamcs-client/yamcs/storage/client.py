from yamcs.core.client import BaseClient
from yamcs.protobuf.rest import rest_pb2
from yamcs.storage.model import Bucket, ObjectListing


class Client(object):

    def __init__(self, address, **kwargs):
        super(Client, self).__init__()
        self._client = BaseClient(address, **kwargs)

    def list_buckets(self, instance):
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self._client.get_proto(path='/buckets/' + instance)
        message = rest_pb2.ListBucketsResponse()
        message.ParseFromString(response.content)
        buckets = getattr(message, 'bucket')
        return iter([
            Bucket(bucket, instance, self) for bucket in buckets])

    def list_objects(self, instance, bucket_name, prefix=None, delimiter=None):
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
        req = rest_pb2.CreateBucketRequest()
        req.name = bucket_name
        url = '/buckets/{}'.format(instance)
        self._client.post_proto(url, data=req.SerializeToString())

    def remove_bucket(self, instance, bucket_name):
        url = '/buckets/{}/{}'.format(instance, bucket_name)
        self._client.delete_proto(url)

    def download_object(self, instance, bucket_name, object_name):
        url = '/buckets/{}/{}/{}'.format(instance, bucket_name, object_name)
        response = self._client.get_proto(path=url)
        return response.content

    def upload_object(self, instance, bucket_name, object_name, file_obj,
                      content_type=None):
        url = '/buckets/{}/{}/{}'.format(instance, bucket_name, object_name)
        with open(file_obj, 'rb') as f:
            if content_type:
                files = {object_name: (object_name, f, content_type)}
            else:
                files = {object_name: (object_name, f)}
            self._client.request(path=url, method='post', files=files)

    def remove_object(self, instance, bucket_name, object_name):
        url = '/buckets/{}/{}/{}'.format(instance, bucket_name, object_name)
        self._client.delete_proto(url)
