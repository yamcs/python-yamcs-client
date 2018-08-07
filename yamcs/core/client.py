import requests


class BaseClient(object):

    def __init__(self, address, credentials):
        """
        :param str address: The address of Yamcs in the format 'hostname:port'
        """
        self.address = address
        self.credentials = credentials

        self.api_root = 'http://{}/api'.format(address)
        self.ws_root = 'ws://{}/_websocket'.format(address)

    def _get_proto(self, path, params=None, headers=None):
        if headers is None:
            headers = {}
        headers = dict(headers)
        headers['Accept'] = 'application/protobuf'

        return self._request('get', path, params, headers)

    def _put_proto(self, path, params=None, headers=None):
        if headers is None:
            headers = {}
        headers = dict(headers)
        headers['Content-Type'] = 'application/protobuf'
        headers['Accept'] = 'application/protobuf'

        return self._request('put', path, params, headers)

    def _patch_proto(self, path, params=None, headers=None):
        if headers is None:
            headers = {}
        headers = dict(headers)
        headers['Content-Type'] = 'application/protobuf'
        headers['Accept'] = 'application/protobuf'

        return self._request('patch', path, params, headers)

    def _post_proto(self, path, params=None, headers=None):
        if headers is None:
            headers = {}
        headers = dict(headers)
        headers['Content-Type'] = 'application/protobuf'
        headers['Accept'] = 'application/protobuf'

        return self._request('post', path, params, headers)

    def _delete_proto(self, path, params=None, headers=None):
        if headers is None:
            headers = {}
        headers = dict(headers)
        headers['Accept'] = 'application/protobuf'

        return self._request('delete', path, params, headers)

    def _request(self, method, path, params=None, headers=None):
        path = '{}/{}'.format(self.api_root, path)
        response = requests.request(
            method, path, params=params, headers=headers)
        response.raise_for_status()
        return response
