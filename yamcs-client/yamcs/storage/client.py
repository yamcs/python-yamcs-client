from yamcs.core.client import BaseClient
from yamcs.protobuf.rest import rest_pb2
from yamcs.storage.model import Bucket, ObjectListing


class Client(object):

    def __init__(self, address, **kwargs):
        super(Client, self).__init__()
        self._client = BaseClient(address, **kwargs)

    def list_global_buckets(self):
        return self.list_buckets('_global')

    def list_buckets(self, instance):
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self._client.get_proto(path='/buckets/' + instance)
        message = rest_pb2.ListBucketsResponse()
        message.ParseFromString(response.content)
        buckets = getattr(message, 'bucket')
        return iter([
            Bucket(bucket, instance, self) for bucket in buckets])

    def list_global_objects(self, bucket_name, **kwargs):
        return self.list_objects('_global', bucket_name, **kwargs)

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
        return ObjectListing(message)

    def create_bucket(self, instance, bucket_name):
        req = rest_pb2.CreateBucketRequest()
        req.name = bucket_name
        url = '/buckets/{}'.format(instance)
        self._client.post_proto(url, data=req.SerializeToString())

    def create_global_bucket(self, bucket_name):
        self.create_bucket('_global', bucket_name)

    def remove_bucket(self, instance, bucket_name):
        url = '/buckets/{}/{}'.format(instance, bucket_name)
        self._client.delete_proto(url)

    def remove_global_bucket(self, bucket_name):
        self.remove_bucket('_global', bucket_name)
