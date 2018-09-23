import pkg_resources
import requests
from google.protobuf.message import DecodeError

from yamcs.core.auth import Credentials
from yamcs.core.exceptions import NotFound, Unauthorized, YamcsError
from yamcs.protobuf.web import web_pb2


def _convert_credentials(token_url, username, password):
    """
    Converts username/password credentials to token credentials by
    using Yamcs as the authenticaton server.
    """
    response = requests.post(token_url, data={
        'grant_type': 'password',
        'username': username,
        'password': password,
    })
    if response.status_code == 401:
        raise Unauthorized('401 Client Error: Unauthorized')
    elif response.status_code == 200:
        d = response.json()
        return Credentials(access_token=d['access_token'],
                           refresh_token=d['refresh_token'])
    else:
        raise YamcsError('{} Server Error'.format(response.status_code))


class BaseClient(object):

    def __init__(self, address, ssl=False, credentials=None, user_agent=None):
        self.address = address
        if ssl:
            self.auth_root = 'https://{}/auth'.format(address)
            self.api_root = 'https://{}/api'.format(address)
            self.ws_root = 'wss://{}/_websocket'.format(address)
        else:
            self.auth_root = 'http://{}/auth'.format(address)
            self.api_root = 'http://{}/api'.format(address)
            self.ws_root = 'ws://{}/_websocket'.format(address)

        self.session = requests.Session()

        if credentials:
            if credentials.username:  # Convert u/p to bearer
                token_url = self.auth_root + '/token'
                credentials = _convert_credentials(
                    token_url, credentials.username, credentials.password)

            self.session.headers.update({
                'Authorization': 'Bearer ' + credentials.access_token
            })

        if not user_agent:
            dist = pkg_resources.get_distribution('yamcs-client')
            user_agent = 'yamcs-python-client v' + dist.version
        self.session.headers.update({'User-Agent': user_agent})

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
        response = self.session.request(method, path, **kwargs)
        if 200 <= response.status_code < 300:
            return response

        exception_message = web_pb2.RestExceptionMessage()
        try:
            exception_message.ParseFromString(response.content)
        except DecodeError:
            pass

        if response.status_code == 401:
            raise Unauthorized('401 Client Error: Unauthorized')
        elif response.status_code == 404:
            raise NotFound('404 Client Error: {}'.format(
                exception_message.msg))
        elif 400 <= response.status_code < 500:
            raise YamcsError('{} Client Error: {}'.format(
                response.status_code, exception_message.msg))
        raise YamcsError('{} Server Error: {}'.format(
            response.status_code, exception_message.msg))
