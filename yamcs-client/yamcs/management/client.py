import functools

from yamcs.core.client import BaseClient
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.management import management_pb2
from yamcs.protobuf.monitoring import monitoring_pb2


def _wrap_callback_parse_time_info(callback, message):
    """
    Wraps a user callback to parse TimeInfo
    from a WebSocket data message
    """
    if message.type == message.REPLY:
        time_response = monitoring_pb2.TimeSubscriptionResponse()
        time_response.ParseFromString(message.reply.data)
        callback(time_response.timeInfo)
    elif message.type == message.DATA:
        if message.data.type == yamcs_pb2.TIME_INFO:
            time_message = getattr(message.data, 'timeInfo')
            callback(time_message)


class ManagementClient(object):

    @classmethod
    def data_link_path(cls, instance, link):
        """
        Return  the resource path for a data link.
        """
        return 'links/{}/{}'.format(instance, link)

    def __init__(self, address, **kwargs):
        super(ManagementClient, self).__init__()
        self._client = BaseClient(address, **kwargs)

    def list_data_links(self, parent):
        """
        Lists the data links visible to this client.

        Data links are returned in random order.

        :param str parent: The instance name
        :rtype: LinkInfo iterator
        """

        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self._client.get_proto(path='links/' + parent)
        message = management_pb2.ListLinksResponse()
        message.ParseFromString(response.content)
        links = getattr(message, 'link')
        return iter(links)

    def get_data_link(self, name):
        """
        Gets a single data link by its unique name.

        :param str name: The name of the data link. For example: ``links/:instance/:link``
        :rtype: :class:`yamcs.protobuf.management.management_pb2.LinkInfo`
        """
        response = self._client.get_proto(name)
        message = management_pb2.LinkInfo()
        message.ParseFromString(response.content)
        return message

    def subscribe_time(self, instance, callback, timeout=60):
        """
        Create a new subscription for receiving time updates of an instance.
        Time updates are emitted at 1Hz.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :rtype: A :class:`~yamcs.core.futures.WebSocketSubscriptionFuture`
                object that can be used to manage the background websocket
                subscription.
        """
        manager = WebSocketSubscriptionManager(self._client, resource='time')
        subscription = WebSocketSubscriptionFuture(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_time_info, callback)
        
        manager.open(wrapped_callback, instance)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription
