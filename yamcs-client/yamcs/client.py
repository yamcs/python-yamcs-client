import functools

from yamcs.archive.client import ArchiveClient
from yamcs.core.client import BaseClient
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.mdb.client import MDBClient
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.rest import rest_pb2
from yamcs.protobuf.web import web_pb2
from yamcs.protobuf.yamcsManagement import yamcsManagement_pb2
from yamcs.tmtc.client import ProcessorClient


def _wrap_callback_parse_time_info(callback, message):
    """
    Wraps a user callback to parse TimeInfo
    from a WebSocket data message
    """
    if message.type == message.REPLY:
        time_response = web_pb2.TimeSubscriptionResponse()
        time_response.ParseFromString(message.reply.data)
        callback(time_response.timeInfo)
    elif message.type == message.DATA:
        if message.data.type == yamcs_pb2.TIME_INFO:
            time_message = getattr(message.data, 'timeInfo')
            callback(time_message)


class YamcsClient(BaseClient):
    """
    Client for accessing core Yamcs resources.

    The only state managed by this client is its connection info to Yamcs.

    :param str address: The address to the Yamcs server in the format 'host:port'
    """

    @classmethod
    def data_link_path(cls, instance, link):
        """
        Return  the resource path for a data link.
        """
        return 'links/{}/{}'.format(instance, link)

    def __init__(self, address, **kwargs):
        super(YamcsClient, self).__init__(address, **kwargs)

    def get_mdb(self, instance):
        """
        Return an object for working with the MDB for the specified instance.

        :param str instance: A Yamcs instance name.
        :rtype: :class:`.MDBClient`
        """
        return MDBClient(self, instance)

    def get_archive(self, instance):
        """
        Return an object for working with the Archive of the specified instance.

        :param str instance: A Yamcs instance name.
        :rtype: :class:`.ArchiveClient`
        """
        return ArchiveClient(self, instance)

    def get_processor(self, instance, processor):
        """
        Return an object for working with a specific Yamcs processor.

        :param str instance: A Yamcs instance name.
        :param str processor: A processor name within that instance.
        :rtype: :class:`.ProcessorClient`
        """
        return ProcessorClient(self, instance, processor)

    def list_data_links(self, parent):
        """
        Lists the data links visible to this client.

        Data links are returned in random order.

        :param str parent: The instance name
        :rtype: :class:`yamcs.protobuf.rest.rest_pb2.LinkInfo` iterator
        """

        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.get_proto(path='links/' + parent)
        message = rest_pb2.ListLinkInfoResponse()
        message.ParseFromString(response.content)
        links = getattr(message, 'link')
        return iter(links)

    def get_data_link(self, name):
        """
        Gets a single data link by its unique name.

        :param str name: The name of the data link. For example: ``links/:instance/:link``
        :rtype: :class:`yamcs.protobuf.rest.rest_pb2.LinkInfo`
        """
        response = self.get_proto(name)
        message = yamcsManagement_pb2.LinkInfo()
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
        manager = WebSocketSubscriptionManager(self, resource='time')
        subscription = WebSocketSubscriptionFuture(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_time_info, callback)

        manager.open(wrapped_callback, instance)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription
