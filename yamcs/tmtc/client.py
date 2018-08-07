import functools

from yamcs.core.client import BaseClient
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.types import yamcs_pb2


def _wrap_callback_parse_parameter_data(callback, message):
    """
    Wraps a user callback to parse ParameterData
    from a WebSocket data message
    """
    if message.type == message.DATA:
        if message.data.type == yamcs_pb2.PARAMETER:
            parameter_data_message = getattr(message.data, 'parameterData')
            callback(parameter_data_message)

class ProcessorClient(BaseClient):

    @classmethod
    def data_link_path(cls, instance, link):
        """
        Return the resource path for a data link.
        """
        return 'links/{}/{}'.format(instance, link)

    def __init__(self, address, credentials=None):
        super(ProcessorClient, self).__init__(
            address, credentials=credentials)

    def subscribe_parameters(self, instance, callback):
        """
        Create a new subscription for receiving value updates of a set of parameters.
        Time updates are emitted at 1Hz.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :rtype: A :class:`~yamcs.core.futures.Future` object that can be
                used to manage the background websocket subscription.
        """
        manager = WebSocketSubscriptionManager(self, None)
        future = WebSocketSubscriptionFuture(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_parameter_data, callback)
        manager.open(wrapped_callback)
        return future
