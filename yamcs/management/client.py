from yamcs.core.client import BaseClient
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.types import management_pb2


class ManagementClient(BaseClient):

    @classmethod
    def data_link_path(cls, instance, link):
        """
        Return  the resource path for a data link.
        """
        return 'links/{}/{}'.format(instance, link)

    def __init__(self, host, port, credentials=None):
        super(ManagementClient, self).__init__(
            host=host, port=port, credentials=credentials)

    def list_data_links(self, parent):
        """
        Lists the data links visible to this client.

        Data links are returned in random order.

        :param str parent: The instance name
        :rtype: LinkInfo iterator
        """

        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self._get_proto(path='links/' + parent)
        message = management_pb2.ListLinksResponse()
        message.ParseFromString(response.content)
        links = getattr(message, 'link')
        return iter(links)

    def get_data_link(self, name):
        """
        Gets a single data link by its unique name.

        :param str name: The name of the data link. For example: ``links/:instance/:link``
        :rtype: :class:`yamcs.types.management_pb2.LinkInfo`
        """
        response = self._get_proto(name)
        message = management_pb2.LinkInfo()
        message.ParseFromString(response.content)
        return message
    
    def subscribe_time(self, instance, callback):
        """
        Create a new subscription for receiving time updates of an instance.
        Time updates are emitted at 1Hz.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :rtype: :class:`yamcs.core.futures.Future` A Future object that can be
                used to manage the background websocket subscription.
        """
        manager = WebSocketSubscriptionManager(self, None)
        
        manager.open(callback)