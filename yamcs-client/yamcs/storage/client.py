import logging

import requests

log = logging.getLogger(__name__)


class Client(object):

    def __init__(self, host='localhost', port=8090):
        self.host = host
        self.port = port
        self.api_root = 'http://{}:{}/api'.format(host, port)

    def get_bucket(self):
        pass

    def request(self, method, api_path):
        response = requests.request(method, '{}{}'.format(self.api_root, api_path))
        response.raise_for_status()
        return response
