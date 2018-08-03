import logging

import requests

from .InstanceRoute import InstanceRoute
from .proto.yamcsManagement_pb2 import YamcsInstances

log = logging.getLogger(__name__)


class YamcsClient(object):

    def __init__(self, host='localhost', port=8090):
        self.host = host
        self.port = port
        self.api_root = 'http://{}:{}/api'.format(host, port)

    def instance(self, name):
        return InstanceRoute(name, self)

    def get_instances(self):
        response = self.get('/instances')
        msg = YamcsInstances()
        msg.ParseFromString(response.content)
        return msg.instance

    def delete(self, api_path):
        return self.request('delete', api_path)

    def get(self, api_path):
        return self.request('get', api_path)

    def patch(self, api_path):
        return self.request('patch', api_path)

    def post(self, api_path):
        return self.request('post', api_path)

    def request(self, method, api_path):
        response = requests.request('get', '{}{}'.format(self.api_root, api_path), headers={
            'Accept': 'application/protobuf'
        })
        response.raise_for_status()
        return response
