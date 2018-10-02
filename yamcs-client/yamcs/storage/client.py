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

    def list_global_objects(self, bucket_name):
        return self.list_objects('_global', bucket_name)

    def list_objects(self, instance, bucket_name):
        url = '/buckets/{}/{}'.format(instance, bucket_name)
        response = self._client.get_proto(path=url)
        message = rest_pb2.ListObjectsResponse()
        message.ParseFromString(response.content)
        return ObjectListing(message)
