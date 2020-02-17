import functools

import requests
from google.protobuf import timestamp_pb2

from yamcs.archive.client import ArchiveClient
from yamcs.core.client import BaseClient
from yamcs.core.exceptions import ConnectionFailure
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.helpers import parse_isostring, to_isostring
from yamcs.core.subscriptions import (WebSocketSubscriptionManager,
                                      WebSocketSubscriptionManagerV2)
from yamcs.mdb.client import MDBClient
from yamcs.model import (AuthInfo, Cop1Config, Cop1Status, Event, Instance,
                         InstanceTemplate, Link, LinkEvent, Processor,
                         ServerInfo, Service, UserInfo)
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.archive import archive_pb2
from yamcs.protobuf.cop1 import cop1_pb2
from yamcs.protobuf.iam import iam_pb2
from yamcs.protobuf.processing import processing_pb2
from yamcs.protobuf.time import time_service_pb2
from yamcs.protobuf.web import auth_pb2, general_service_pb2, websocket_pb2
from yamcs.protobuf.yamcsManagement import yamcsManagement_pb2
from yamcs.tmtc.client import ProcessorClient


def _wrap_callback_parse_time_info(subscription, on_data, message):
    """
    Wraps a user callback to parse TimeInfo
    from a WebSocket data message
    """
    time_message = timestamp_pb2.Timestamp()
    message.Unpack(time_message)
    #pylint: disable=no-member
    time = time_message.ToDatetime()
    #pylint: disable=protected-access
    subscription._process(time)
    if on_data:
        on_data(time)


def _wrap_callback_parse_event(on_data, message):
    """
    Wraps a user callback to parse Events
    from a WebSocket data message
    """
    if message.type == message.DATA:
        if message.data.type == yamcs_pb2.EVENT:
            event = Event(getattr(message.data, 'event'))
            on_data(event)


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


def _wrap_callback_parse_cop1_status(subscription, on_data, message):
    """
    Wraps a user callback to parse Cop1Status
    from a WebSocket data message
    """
    if message.type == message.DATA:
        if message.data.type == yamcs_pb2.COP1_STATUS:
            cop1_status = Cop1Status(getattr(message.data, 'cop1Status'))
            if on_data:
                on_data(cop1_status)


class TimeSubscription(WebSocketSubscriptionFuture):
    """
    Local object providing access to time updates.

    A subscription object stores the last time info.
    """

    def __init__(self, manager):
        super(TimeSubscription, self).__init__(manager)

        self.time = None
        """
        The last time info.

        :type: :class:`~datetime.datetime`
        """

    def _process(self, time):
        self.time = time


class DataLinkSubscription(WebSocketSubscriptionFuture):
    """
    Local object providing access to data link updates.

    A subscription object stores the last link info for
    each link.
    """

    def __init__(self, manager):
        super(DataLinkSubscription, self).__init__(manager)

        self._cache = {}
        """Link cache keyed by name."""

    def get_data_link(self, name):
        """
        Returns the latest link state.

        :param str name: Identifying name of the data link
        :rtype: .Link
        """
        if name in self._cache:
            return self._cache[name]
        return None

    def list_data_links(self):
        """
        Returns a snapshot of all instance links.

        :rtype: .Link[]
        """
        return [self._cache[k] for k in self._cache]

    def _process(self, link_event):
        link = link_event.link
        if link_event.event_type == 'UNREGISTERED':
            del self._cache[link.name]
        else:
            self._cache[link.name] = link


class Cop1Subscription(WebSocketSubscriptionFuture):
    """
    Local object providing access to COP1 status updates.
    """

    def add(self, instance, link_name):
        """
        Add one link to this subscription.

        :param string instance: The Yamcs instance containing the link to be added
        :param string link_name: the name of the link to be added
        """

        # Verify that we already know our assigned subscription_id

        options = websocket_pb2.Cop1SubscriptionRequest()
        options.instance = instance
        options.linkName = link_name

        self._manager.send('subscribe', options)

    def remove(self, instance, link_name):
        """
        Remove one link from this subscription.

        :param string instance: The Yamcs instance containing the link to be removed
        :param string link_name: the name of the link to be removed
        """

        # Verify that we already know our assigned subscription_id

        options = websocket_pb2.Cop1SubscriptionRequest()
        options.instance = instance
        options.linkName = link_name

        self._manager.send('unsubscribe', options)


class YamcsClient(BaseClient):
    """
    Client for accessing core Yamcs resources.

    The only state managed by this client is its connection info to Yamcs.
    """

    def __init__(self, address, **kwargs):
        """
        :param str address: The address of Yamcs in the format 'hostname:port'
        :param Optional[bool] tls: Whether TLS encryption is expected
        :param Optional[bool] tls_verify: Whether server certificate verification is enabled
                                          (only applicable if ``tls=True``)
        :param Optional[.Credentials] credentials: Credentials for when the server is secured
        :param Optional[str] user_agent: Optionally override the default user agent
        """
        super(YamcsClient, self).__init__(address, **kwargs)

    def get_time(self, instance):
        """
        Return the current mission time for the specified instance.

        :rtype: ~datetime.datetime
        """
        url = '/instances/{}'.format(instance)
        response = self.get_proto(url)
        message = yamcsManagement_pb2.YamcsInstance()
        message.ParseFromString(response.content)
        if message.HasField('missionTime'):
            return parse_isostring(message.missionTime)
        return None

    def get_server_info(self):
        """
        Return general server info.

        :rtype: .ServerInfo
        """
        response = self.get_proto(path='')
        message = general_service_pb2.GetGeneralInfoResponse()
        message.ParseFromString(response.content)
        return ServerInfo(message)

    def get_auth_info(self):
        """
        Returns general authentication information. This operation
        does not require authenticating and is useful to test
        if a server requires authentication or not.

        :rtype: .AuthInfo
        """
        try:
            response = self.session.get(self.auth_root, headers={
                'Accept': 'application/protobuf'
            })
            message = auth_pb2.AuthInfo()
            message.ParseFromString(response.content)
            return AuthInfo(message)
        except requests.exceptions.ConnectionError:
            raise ConnectionFailure('Connection to {} refused'.format(self.address))

    def get_user_info(self):
        """
        Get information on the authenticated user.

        :rtype: .UserInfo
        """
        response = self.get_proto(path='/user')
        message = iam_pb2.UserInfo()
        message.ParseFromString(response.content)
        return UserInfo(message)

    def get_mdb(self, instance):
        """
        Return an object for working with the MDB of the specified instance.

        :param str instance: A Yamcs instance name.
        :rtype: .MDBClient
        """
        return MDBClient(self, instance)

    def get_archive(self, instance):
        """
        Return an object for working with the Archive of the specified instance.

        :param str instance: A Yamcs instance name.
        :rtype: .ArchiveClient
        """
        return ArchiveClient(self, instance)

    def create_instance(self, name, template, args=None, labels=None):
        """
        Create a new instance based on an existing template. This method blocks
        until the instance is fully started.

        :param str instance: A Yamcs instance name.
        :param str template: The name of an existing template.
        """
        req = yamcsManagement_pb2.CreateInstanceRequest()
        req.name = name
        req.template = template
        if args:
            for k in args:
                req.templateArgs[k] = args[k]
        if labels:
            for k in labels:
                req.labels[k] = labels[k]
        url = '/instances'
        self.post_proto(url, data=req.SerializeToString())

    def list_instance_templates(self):
        """
        List the available instance templates.
        """
        response = self.get_proto(path='/instance-templates')
        message = yamcsManagement_pb2.ListInstanceTemplatesResponse()
        message.ParseFromString(response.content)
        templates = getattr(message, 'templates')
        return iter([InstanceTemplate(template) for template in templates])

    def list_services(self, instance):
        """
        List the services for an instance.

        :param str instance: A Yamcs instance name.
        :rtype: ~collections.Iterable[.Service]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        url = '/services/{}'.format(instance)
        response = self.get_proto(path=url)
        message = yamcsManagement_pb2.ListServicesResponse()
        message.ParseFromString(response.content)
        services = getattr(message, 'services')
        return iter([Service(service) for service in services])

    def start_service(self, instance, service):
        """
        Starts a single service.

        :param str instance: A Yamcs instance name.
        :param str service: The name of the service.
        """
        url = '/services/{}/{}:start'.format(instance, service)
        self.post_proto(url)

    def stop_service(self, instance, service):
        """
        Stops a single service.

        :param str instance: A Yamcs instance name.
        :param str service: The name of the service.
        """
        url = '/services/{}/{}:stop'.format(instance, service)
        self.post_proto(url)

    def list_processors(self, instance=None):
        """
        Lists the processors.

        Processors are returned in lexicographical order.

        :param Optional[str] instance: A Yamcs instance name.
        :rtype: ~collections.Iterable[.Processor]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        url = '/processors'
        if instance:
            url += '?instance=' + instance
        response = self.get_proto(path=url)
        message = processing_pb2.ListProcessorsResponse()
        message.ParseFromString(response.content)
        processors = getattr(message, 'processors')
        return iter([Processor(processor) for processor in processors])

    def get_processor(self, instance, processor):
        """
        Return an object for working with a specific Yamcs processor.

        :param str instance: A Yamcs instance name.
        :param str processor: A processor name within that instance.
        :rtype: .ProcessorClient
        """
        return ProcessorClient(self, instance, processor)

    def list_instances(self):
        """
        Lists the instances.

        Instances are returned in lexicographical order.

        :rtype: ~collections.Iterable[.Instance]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.get_proto(path='/instances')
        message = yamcsManagement_pb2.ListInstancesResponse()
        message.ParseFromString(response.content)
        instances = getattr(message, 'instances')
        return iter([Instance(instance) for instance in instances])

    def start_instance(self, instance):
        """
        Starts a single instance.

        :param str instance: A Yamcs instance name.
        """
        url = '/instances/{}:start'.format(instance)
        self.post_proto(url)

    def stop_instance(self, instance):
        """
        Stops a single instance.

        :param str instance: A Yamcs instance name.
        """
        url = '/instances/{}:stop'.format(instance)
        self.post_proto(url)

    def restart_instance(self, instance):
        """
        Restarts a single instance.

        :param str instance: A Yamcs instance name.
        """
        url = '/instances/{}:restart'.format(instance)
        self.post_proto(url)

    def list_data_links(self, instance):
        """
        Lists the data links visible to this client.

        Data links are returned in random order.

        :param str instance: A Yamcs instance name.
        :rtype: ~collections.Iterable[.Link]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.get_proto(path='/links/' + instance)
        message = yamcsManagement_pb2.ListLinksResponse()
        message.ParseFromString(response.content)
        links = getattr(message, 'links')
        return iter([Link(link) for link in links])

    def send_event(self, instance, message, event_type=None, time=None,
                   severity='info', source=None, sequence_number=None):
        """
        Post a new event.

        :param str instance: A Yamcs instance name.
        :param str message: Event message.
        :param Optional[str] event_type: Type of event.

        :param severity: The severity level of the event. One of ``info``,
                         ``watch``, ``warning``, ``critical`` or ``severe``.
                         Defaults to ``info``.
        :type severity: Optional[str]

        :param time: Time of the event. If unspecified, defaults to mission time.
        :type time: Optional[~datetime.datetime]

        :param source: Source of the event. Useful for grouping events in the
                       archive. When unset this defaults to ``User``.
        :type source: Optional[str]

        :param sequence_number: Sequence number of this event. This is primarily
                                used to determine unicity of events coming from
                                the same source. If not set Yamcs will
                                automatically assign a sequential number as if
                                every submitted event is unique.
        :type sequence_number: Optional[int]
        """
        req = archive_pb2.CreateEventRequest()
        req.message = message
        req.severity = severity
        if event_type:
            req.type = event_type
        if time:
            req.time = to_isostring(time)
        if source:
            req.source = source
        if sequence_number is not None:
            req.sequence_number = sequence_number

        url = '/archive/{}/events'.format(instance)
        self.post_proto(url, data=req.SerializeToString())

    def get_data_link(self, instance, link):
        """
        Gets a single data link.

        :param str instance: A Yamcs instance name.
        :param str link: The name of the data link.
        :rtype: .Link
        """
        response = self.get_proto('/links/{}/{}'.format(instance, link))
        message = yamcsManagement_pb2.LinkInfo()
        message.ParseFromString(response.content)
        return Link(message)

    def enable_data_link(self, instance, link):
        """
        Enables a data link.

        :param str instance: A Yamcs instance name.
        :param str link: The name of the data link.
        """
        req = yamcsManagement_pb2.EditLinkRequest()
        req.state = 'enabled'
        url = '/links/{}/{}'.format(instance, link)
        self.patch_proto(url, data=req.SerializeToString())

    def disable_data_link(self, instance, link):
        """
        Disables a data link.

        :param str instance: A Yamcs instance name.
        :param str link: The name of the data link.
        """
        req = yamcsManagement_pb2.EditLinkRequest()
        req.state = 'disabled'
        url = '/links/{}/{}'.format(instance, link)
        self.patch_proto(url, data=req.SerializeToString())

    def create_data_link_subscription(self, instance, on_data=None, timeout=60):
        """
        Create a new subscription for receiving data link updates of an instance.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param str instance: A Yamcs instance name.

        :param on_data: Function that gets called with
                        :class:`.LinkEvent` updates.
        :type on_data: Optional[Callable[.LinkEvent])

        :param timeout: The amount of seconds to wait for the request to
                        complete.
        :type timeout: Optional[float]

        :return: Future that can be used to manage the background websocket
                 subscription.
        :rtype: .DataLinkSubscription
        """
        manager = WebSocketSubscriptionManager(self, resource='links')

        # Represent subscription as a future
        subscription = DataLinkSubscription(manager)

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

        :param on_data: Function that gets called with
                        :class:`~datetime.datetime` updates.
        :type on_data: Optional[Callable[~datetime.datetime])

        :param timeout: The amount of seconds to wait for the request to
                        complete.
        :type timeout: Optional[float]

        :return: Future that can be used to manage the background websocket
                 subscription.
        :rtype: .TimeSubscription
        """
        options = time_service_pb2.SubscribeTimeRequest()
        options.instance = instance
        manager = WebSocketSubscriptionManagerV2(self, topic='time', options=options)

        # Represent subscription as a future
        subscription = TimeSubscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_time_info, subscription, on_data)

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def create_event_subscription(self, instance, on_data, timeout=60):
        """
        Create a new subscription for receiving events of an instance.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param str instance: A Yamcs instance name

        :param on_data: Function that gets called on each :class:`.Event`.
        :type on_data: Optional[Callable[.Event])

        :param timeout: The amount of seconds to wait for the request to
                        complete.
        :type timeout: Optional[float]

        :return: Future that can be used to manage the background websocket
                 subscription.
        :rtype: .WebSocketSubscriptionFuture
        """
        manager = WebSocketSubscriptionManager(self, resource='events')

        # Represent subscription as a future
        subscription = WebSocketSubscriptionFuture(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_event, on_data)

        manager.open(wrapped_callback, instance)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def get_cop1_config(self, instance, link):
        """
        Gets the COP1 configuration for a data link.

        :param str instance: A Yamcs instance name.
        :param str link: The name of the data link.
        :rtype: .Cop1Config
        """
        response = self.get_proto('/cop1/{}/{}/config'.format(instance, link))
        message = cop1_pb2.Cop1Config()
        message.ParseFromString(response.content)
        return Cop1Config(message)

    def set_cop1_config(self, instance, link, cop1_config):
        """
        Sets the COP1 configuration for a data link.

        :param str instance: A Yamcs instance name.
        :param str link: The name of the data link.
        :param Cop1Config cop1_config: The config to be set
        """
        req = cop1_pb2.SetConfigRequest()
        req.cop1Config.CopyFrom(cop1_config._proto)

        url = '/cop1/{}/{}/config'.format(instance, link)
        self.patch_proto(url, data=req.SerializeToString())

    def disable_cop1(self, instance, link, set_bypass_all=True):
        """
        Disable COP1 for a data link.

        :param str instance: A Yamcs instance name.
        :param str link: The name of the data link.
        :param bool set_bypass_all: If True(default) then all frames will have the Bypass flag activated (i.e. they will be BD frames)
        """
        req = cop1_pb2.DisableRequest()
        req.setBypassAll = set_bypass_all
        url = '/cop1/{}/{}:disable'.format(instance, link)
        self.post_proto(url, data=req.SerializeToString())

    def initialize_cop1(self, instance, link, type, clcw_wait_timeout=None, v_r=None):
        """
        Initialize COP1.

        :param str instance: A Yamcs instance name.
        :param str link: The name of the data link.
        :param str type: One of  WITH_CLCW_CHECK,  WITHOUT_CLCW_CHECK, UNLOCK, SET_VR
        :param int clcw_wait_timeout: timeout in seconds used for the reception of CLCS, required in case type = WITH_CLCW_CHECK
        :param int v_r: value of v(R) in case type = SET_VR
        """
        req = cop1_pb2.InitializeRequest()
        req.type = cop1_pb2.InitializationType.Value(type)

        if clcw_wait_timeout is not None:
            req.clcwCheckInitializeTimeout = int(1000 * clcw_wait_timeout)
        if v_r is not None:
            req.vR = v_r

        url = '/cop1/{}/{}:initialize'.format(instance, link)
        self.post_proto(url, data=req.SerializeToString())

    def resume_cop1(self, instance, link, set_bypass_all=True):
        """
        Disable COP1 for a data link.

        :param str instance: A Yamcs instance name.
        :param str link: The name of the data link.
        :param bool set_bypass_all: If True(default) then all frames will have the Bypass flag activated (i.e. they will be BD frames)
        """
        req = cop1_pb2.ResumeRequest()
        url = '/cop1/{}/{}:resume'.format(instance, link)
        self.post_proto(url, data=req.SerializeToString())

    def get_cop1_status(self, instance, link):
        """
        Gets the COP1 status for a data link.

        :param str instance: A Yamcs instance name.
        :param str link: The name of the data link.
        :rtype: .Cop1Status
        """
        response = self.get_proto('/cop1/{}/{}/status'.format(instance, link))
        message = cop1_pb2.Cop1Status()
        message.ParseFromString(response.content)
        return Cop1Status(message)

    def create_cop1_subscription(self, instance, linkName, on_data, timeout=60):
        """
        Create a new subscription for receiving status of the COP1 link.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param str instance: A Yamcs instance name

        :param str linkName: The link name (has to be of type Cop1TcPacketHandler)
        
        :param on_data: Function that gets called on each :class:`.Cop1Status`.
        :type on_data: Optional[Callable[.Cop1Status])

        :param timeout: The amount of seconds to wait for the request to
                        complete.
        :type timeout: Optional[float]

        :return: Future that can be used to manage the background websocket
                 subscription.
        :rtype: .Cop1Subscription
        """
        options = websocket_pb2.Cop1SubscriptionRequest()
        options.instance = instance
        options.linkName = linkName

        manager = WebSocketSubscriptionManager(self, resource='cop1', options=options)

        # Represent subscription as a future
        subscription = Cop1Subscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_cop1_status, subscription, on_data)

        manager.open(wrapped_callback, instance)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription
