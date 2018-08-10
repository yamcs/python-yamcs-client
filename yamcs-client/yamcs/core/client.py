import requests


class BaseClient(object):

    def __init__(self, address, credentials=None, ssl=False):
        """
        :param str address: The address of Yamcs in the format 'hostname:port'
        """
        self.address = address
        self.credentials = credentials

        if ssl:
            self.api_root = 'https://{}/api'.format(address)
            self.ws_root = 'wss://{}/_websocket'.format(address)
        else:
            self.api_root = 'http://{}/api'.format(address)
            self.ws_root = 'ws://{}/_websocket'.format(address)

    def get_proto(self, path, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Accept'] = 'application/protobuf'
        kwargs.update({'headers': headers})
        return self.request('get', path, **kwargs)

    def put_proto(self, path, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Content-Type'] = 'application/protobuf'
        headers['Accept'] = 'application/protobuf'
        kwargs.update({'headers': headers})
        return self.request('put', path, **kwargs)

    def patch_proto(self, path, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Content-Type'] = 'application/protobuf'
        headers['Accept'] = 'application/protobuf'
        kwargs.update({'headers': headers})
        return self.request('patch', path, **kwargs)

    def post_proto(self, path, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Content-Type'] = 'application/protobuf'
        headers['Accept'] = 'application/protobuf'
        kwargs.update({'headers': headers})
        return self.request('post', path, **kwargs)

    def delete_proto(self, path, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Accept'] = 'application/protobuf'
        kwargs.update({'headers': headers})
        return self.request('delete', path, **kwargs)

    def request(self, method, path, **kwargs):
        path = '{}{}'.format(self.api_root, path)
        response = requests.request(method, path, **kwargs)
        response.raise_for_status()
        return response
