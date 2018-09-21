import functools

from yamcs.archive.client import ArchiveClient
from yamcs.core.client import BaseClient
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.helpers import parse_isostring
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.mdb.client import MDBClient
from yamcs.model import Link, LinkEvent
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.rest import rest_pb2
from yamcs.protobuf.web import web_pb2
from yamcs.protobuf.yamcsManagement import yamcsManagement_pb2
from yamcs.tmtc.client import ProcessorClient


def _wrap_callback_parse_time_info(subscription, on_data, message):
    """
    Wraps a user callback to parse TimeInfo
    from a WebSocket data message
    """
    if message.type == message.REPLY:
        time_response = web_pb2.TimeSubscriptionResponse()
        time_response.ParseFromString(message.reply.data)
        time = parse_isostring(time_response.timeInfo.currentTimeUTC)
        #pylint: disable=protected-access
        subscription._process(time)
        if on_data:
            on_data(time)
    elif message.type == message.DATA:
        if message.data.type == yamcs_pb2.TIME_INFO:
            time_message = getattr(message.data, 'timeInfo')
            time = parse_isostring(time_message.currentTimeUTC)
            #pylint: disable=protected-access
            subscription._process(time)
            if on_data:
                on_data(time)


def _wrap_callback_parse_link_event(subscription, on_data, message):
    """
    Wraps a user callback to parse LinkEvents
    from a WebSocket data message
    """
    if message.type == message.DATA:
        if message.data.type == yamcs_pb2.LINK_EVENT:
            link_message = getattr(message.data, 'linkEvent')
            link_event = LinkEvent(link_message)
            #pylint: disable=protected-access
            subscription._process(link_event)
            if on_data:
                on_data(link_event)


class TimeSubscriptionFuture(WebSocketSubscriptionFuture):
    """
    Local object providing access to time updates.

    A subscription object stores the last time info.
    """

    def __init__(self, manager):
        super(TimeSubscriptionFuture, self).__init__(manager)

        self.time = None
        """The last time info."""

    def _process(self, time):
        self.time = time


class DataLinkSubscriptionFuture(WebSocketSubscriptionFuture):
    """
    Local object providing access to data link updates.

    A subscription object stores the last link info for
    each link.
    """

    def __init__(self, manager):
        super(DataLinkSubscriptionFuture, self).__init__(manager)

        self._cache = {}
        """Link cache keyed by name."""

    def get_data_link(self, name):
        """
        Returns the latest link info.
        """
        if name in self._cache:
            return self._cache[name]
        return None

    def list_data_links(self):
        """
        Returns a snapshot of all instance links.
        """
        return [self._cache[k] for k in self._cache]

    def _process(self, link_event):
        if link_event.event_type == 'UNREGISTERED':
            del self._cache[link_event.link.name]
        else:
            self._cache[link_event.link.name] = link_event.link


class YamcsClient(BaseClient):
    """
    Client for accessing core Yamcs resources.

    The only state managed by this client is its connection info to Yamcs.

    :param str address: The address to the Yamcs server in the format 'host:port'
    """

    def __init__(self, address, **kwargs):
        super(YamcsClient, self).__init__(address, **kwargs)

    def get_time(self, instance):
        """
        Return the current mission time for the specified instance.
        :rtype :class:`datetime`
        """
        url = '/instances/{}'.format(instance)
        response = self.get_proto(url)
        message = yamcsManagement_pb2.YamcsInstance()
        message.ParseFromString(response.content)
        if message.HasField('missionTime'):
            return parse_isostring(message.missionTime)
        return None

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

    def list_data_links(self, instance):
        """
        Lists the data links visible to this client.

        Data links are returned in random order.

        :param str instance: A Yamcs instance name
        :rtype: :class:`.LinkEvent` iterator
        """

        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.get_proto(path='links/' + instance)
        message = rest_pb2.ListLinkInfoResponse()
        message.ParseFromString(response.content)
        links = getattr(message, 'link')
        return iter(links)

    def get_data_link(self, instance, link):
        """
        Gets a single data link.

        :param str instance: A Yamcs instance name
        :param str link: The name of the data link.
        :rtype: :class:`.Link`
        """
        response = self.get_proto('links/{}/{}'.format(instance, link))
        message = yamcsManagement_pb2.LinkInfo()
        message.ParseFromString(response.content)
        return Link(message)


    def create_data_link_subscription(self, instance, on_data=None, timeout=60):
        """
        Create a new subscription for receiving data link updates of an instance.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param str instance: A Yamcs instance name
        :param on_data: Function that gets called on each message.
        :param float timeout: The amount of seconds to wait for the request
                              to complete.
        :rtype: A :class:`.DataLinkSubscriptionFuture`
                object that can be used to manage the background websocket
                subscription.
        """
        manager = WebSocketSubscriptionManager(self, resource='links')
        
        # Represent subscription as a future
        subscription = DataLinkSubscriptionFuture(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_link_event, subscription, on_data)

        manager.open(wrapped_callback, instance)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription


    def create_time_subscription(self, instance, on_data=None, timeout=60):
        """
        Create a new subscription for receiving time updates of an instance.
        Time updates are emitted at 1Hz.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param str instance: A Yamcs instance name
        :param on_data: Function that gets called on each message.
        :param float timeout: The amount of seconds to wait for the request
                              to complete.
        :rtype: A :class:`.TimeSubscriptionFuture`
                object that can be used to manage the background websocket
                subscription.
        """
        manager = WebSocketSubscriptionManager(self, resource='time')

        # Represent subscription as a future
        subscription = TimeSubscriptionFuture(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_time_info, subscription, on_data)

        manager.open(wrapped_callback, instance)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription
