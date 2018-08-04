import requests


class BaseClient(object):

    def __init__(self, host, port, credentials):
        self.host = host
        self.port = port
        self.credentials = credentials

        self.api_root = 'http://{}:{}/api'.format(host, port)

    def _get(self, path, params=None):
        return self._request('get', path, params)

    def _put(self, path, params=None):
        return self._request('put', path, params)

    def _patch(self, path, params=None):
        return self._request('patch', path, params)

    def _post(self, path, params=None):
        return self._request('post', path, params)

    def _delete(self, path, params=None):
        return self._request('delete', path, params)

    def _request(self, method, path, params=None):
        response = requests.request(method, '{}{}'.format(self.api_root, path), params=params)
        response.raise_for_status()
        return response
