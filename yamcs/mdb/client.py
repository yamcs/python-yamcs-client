import json
import logging

import requests

log = logging.getLogger(__name__)


class Client(object):

    def __init__(self, host, port, instance):
        self.host = host
        self.port = port
        self.instance = instance
        self.api_root = 'http://{}:{}/api'.format(host, port)

    def get_parameters(self):
        response = self.request('get', '/mdb/{}/parameters'.format(self.instance))
        return json.loads(response.content)['parameter']

    def get_parameter(self, name, namespace=None):
        response = self.request('get', '/mdb/{}/parameters'.format(self.instance))
        return response.content

    def request(self, method, api_path):
        response = requests.request(method, '{}{}'.format(self.api_root, api_path))
        response.raise_for_status()
        return response
