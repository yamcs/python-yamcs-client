import logging

from websocket import create_connection

from .exceptions import ConnectionError
from .proto.rest_pb2 import ListParameterInfoResponse


class InstanceRoute(object):
    """
    Owns the websocket connection
    """

    def __init__(self, instance, client, connect=False):
        self.instance = instance
        self.client = client

        self.connected = False
        self.websocket = None

        if connect:
            self.connect_websocket()

    def get_parameters(self):
        response = self.client.get('/mdb/{}/parameters'.format(self.instance))
        msg = ListParameterInfoResponse()
        msg.ParseFromString(response.content)
        return msg.parameter

    def connect_websocket(self):
        try:
            self.websocket = create_connection('ws://localhost:8090/_websocket/simulator')
            self.connected = True
            logging.info('WebSocket connected')
            self.websocket.sock.setblocking(0)  # equivalent to settimeout(0.0)
        except Exception as e:
            self.connected = False
            raise ConnectionError(message=str(e))
