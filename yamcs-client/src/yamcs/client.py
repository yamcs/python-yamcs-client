import functools
import warnings

import requests
from google.protobuf import timestamp_pb2

from yamcs.archive.client import ArchiveClient
from yamcs.core.context import Context
from yamcs.core.exceptions import ConnectionFailure
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.helpers import parse_server_time, to_server_time
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.filetransfer.client import FileTransferClient
from yamcs.link.client import LinkClient
from yamcs.mdb.client import MDBClient
from yamcs.model import (
    AuthInfo,
    Event,
    Instance,
    InstanceTemplate,
    Link,
    LinkEvent,
    Processor,
    ServerInfo,
    Service,
    UserInfo,
)
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.events import events_service_pb2
from yamcs.protobuf.iam import iam_pb2
from yamcs.protobuf.processing import processing_pb2
from yamcs.protobuf.time import time_service_pb2
from yamcs.protobuf.web import auth_pb2, server_service_pb2
from yamcs.protobuf.yamcsManagement import yamcsManagement_pb2
from yamcs.storage.client import StorageClient
from yamcs.tco.client import TCOClient
from yamcs.tmtc.client import ProcessorClient


def _wrap_callback_parse_time_info(subscription, on_data, message):
    """
    Wraps a user callback to parse TimeInfo
    from a WebSocket data message
    """
    pb = timestamp_pb2.Timestamp()
    message.Unpack(pb)
    time = parse_server_time(pb)
    subscription._process(time)
    if on_data:
        on_data(time)


def _wrap_callback_parse_event(on_data, message):
    """
    Wraps a user callback to parse Events
    from a WebSocket data message
    """
    pb = yamcs_pb2.Event()
    message.Unpack(pb)
    event = Event(pb)
    on_data(event)


def _wrap_callback_parse_link_event(subscription, on_data, message):
    """
    Wraps a user callback to parse LinkEvents
    from a WebSocket data message
    """
    pb = yamcsManagement_pb2.LinkEvent()
    message.Unpack(pb)
    link_event = LinkEvent(pb)
    subscription._process(link_event)
    if on_data:
        on_data(link_event)


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


class LinkSubscription(WebSocketSubscriptionFuture):
    """
    Local object providing access to data link updates.

    A subscription object stores the last link info for
    each link.
    """

    def __init__(self, manager):
        super(LinkSubscription, self).__init__(manager)

        self._cache = {}
        """Link cache keyed by name."""

    def get_data_link(self, name):
        """
        Deprecated. Use ``get_link(name)``.
        """
        warnings.warn(
            "Method renamed for consistency. "
            "Use: get_link(name) instead of get_data_link(name)",
            FutureWarning,
        )
        return self.get_link(name)

    def get_link(self, name):
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
        Deprecated. Use ``list_links()``.
        """
        warnings.warn(
            "Method renamed for consistency. "
            "Use: list_links() instead of list_data_links()",
            FutureWarning,
        )
        return self.list_links()

    def list_links(self):
        """
        Returns a snapshot of all instance links.

        :rtype: .Link[]
        """
        return [self._cache[k] for k in self._cache]

    def _process(self, link_event):
        link = link_event.link
        if link_event.event_type == "UNREGISTERED":
            del self._cache[link.name]
        else:
            self._cache[link.name] = link


class YamcsClient:
    """
    Client for accessing core Yamcs resources.
    """

    def __init__(self, address, **kwargs):
        """
        :param str address: The address of Yamcs in the format 'hostname:port'
        :param Optional[bool] tls: Whether TLS encryption is expected
        :param Optional[bool] tls_verify: Whether server certificate verification is
                                          enabled (only applicable if ``tls=True``)
        :param Optional[.Credentials] credentials: Credentials for when the server is
                                                   secured
        :param Optional[str] user_agent: Optionally override the default user agent
        """
        self.ctx = Context(address, **kwargs)

    def get_time(self, instance):
        """
        Return the current mission time for the specified instance.

        :rtype: ~datetime.datetime
        """
        url = f"/instances/{instance}"
        response = self.ctx.get_proto(url)
        message = yamcsManagement_pb2.YamcsInstance()
        message.ParseFromString(response.content)
        if message.HasField("missionTime"):
            return parse_server_time(message.missionTime)
        return None

    def get_server_info(self):
        """
        Return general server info.

        :rtype: .ServerInfo
        """
        response = self.ctx.get_proto(path="")
        message = server_service_pb2.GetServerInfoResponse()
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
            response = self.ctx.session.get(
                self.ctx.auth_root, headers={"Accept": "application/protobuf"}
            )
            message = auth_pb2.AuthInfo()
            message.ParseFromString(response.content)
            return AuthInfo(message)
        except requests.exceptions.ConnectionError:
            raise ConnectionFailure(f"Connection to {self.ctx.address} refused")

    def get_user_info(self):
        """
        Get information on the authenticated user.

        :rtype: .UserInfo
        """
        response = self.ctx.get_proto(path="/user")
        message = iam_pb2.UserInfo()
        message.ParseFromString(response.content)
        return UserInfo(message)

    def get_mdb(self, instance):
        """
        Return an object for working with the MDB of the specified instance.

        :param str instance: A Yamcs instance name.
        :rtype: .MDBClient
        """
        return MDBClient(self.ctx, instance)

    def get_archive(self, instance):
        """
        Return an object for working with the Archive of the specified instance.

        :param str instance: A Yamcs instance name.
        :rtype: .ArchiveClient
        """
        return ArchiveClient(self.ctx, instance)

    def get_file_transfer_client(self, instance):
        """
        Return an object for working with file transfers on a specified instance.

        :param str instance: A Yamcs instance name.
        :rtype: .FileTransferClient
        """
        return FileTransferClient(self.ctx, instance)

    def get_cfdp_client(self, instance):
        """
        Deprecated. Use ``get_file_transfer_client()``.
        """
        warnings.warn(
            "Use get_file_transfer_client() instead of get_cfdp_client()",
            FutureWarning,
        )
        return FileTransferClient(self.ctx, instance)

    def get_tco_client(self, instance, service):
        """
        Return an object for Time Correlation API calls on a specified service.

        :param str instance: A Yamcs instance name.
        :param str service: Target service name.
        :rtype: .TCOClient
        """
        return TCOClient(self.ctx, instance, service)

    def get_storage_client(self, instance="_global"):
        """
        Return an object for working with object storage

        :param str instance: The storage instance.
        :rtype: .StorageClient
        """
        return StorageClient(self.ctx, instance)

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
        url = "/instances"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def list_instance_templates(self):
        """
        List the available instance templates.
        """
        response = self.ctx.get_proto(path="/instance-templates")
        message = yamcsManagement_pb2.ListInstanceTemplatesResponse()
        message.ParseFromString(response.content)
        templates = getattr(message, "templates")
        return iter([InstanceTemplate(template) for template in templates])

    def list_services(self, instance):
        """
        List the services for an instance.

        :param str instance: A Yamcs instance name.
        :rtype: ~collections.abc.Iterable[~yamcs.model.Service]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        url = f"/services/{instance}"
        response = self.ctx.get_proto(path=url)
        message = yamcsManagement_pb2.ListServicesResponse()
        message.ParseFromString(response.content)
        services = getattr(message, "services")
        return iter([Service(service) for service in services])

    def start_service(self, instance, service):
        """
        Starts a single service.

        :param str instance: A Yamcs instance name.
        :param str service: The name of the service.
        """
        url = f"/services/{instance}/{service}:start"
        self.ctx.post_proto(url)

    def stop_service(self, instance, service):
        """
        Stops a single service.

        :param str instance: A Yamcs instance name.
        :param str service: The name of the service.
        """
        url = f"/services/{instance}/{service}:stop"
        self.ctx.post_proto(url)

    def list_processors(self, instance=None):
        """
        Lists the processors.

        Processors are returned in lexicographical order.

        :param Optional[str] instance: A Yamcs instance name.
        :rtype: ~collections.abc.Iterable[.Processor]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        url = "/processors"
        if instance:
            url += "?instance=" + instance
        response = self.ctx.get_proto(path=url)
        message = processing_pb2.ListProcessorsResponse()
        message.ParseFromString(response.content)
        processors = getattr(message, "processors")
        return iter([Processor(processor) for processor in processors])

    def get_processor(self, instance, processor):
        """
        Return an object for working with a specific Yamcs processor.

        :param str instance: A Yamcs instance name.
        :param str processor: A processor name within that instance.
        :rtype: .ProcessorClient
        """
        return ProcessorClient(self.ctx, instance, processor)

    def get_link(self, instance, link):
        """
        Return an object for working with a specific Yamcs link.

        :param str instance: A Yamcs instance name.
        :param str link: A link name within that instance.
        :rtype: .LinkClient
        """
        return LinkClient(self.ctx, instance, link)

    def list_instances(self):
        """
        Lists the instances.

        Instances are returned in lexicographical order.

        :rtype: ~collections.abc.Iterable[.Instance]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(path="/instances")
        message = yamcsManagement_pb2.ListInstancesResponse()
        message.ParseFromString(response.content)
        instances = getattr(message, "instances")
        return iter([Instance(instance) for instance in instances])

    def start_instance(self, instance):
        """
        Starts a single instance.

        :param str instance: A Yamcs instance name.
        """
        url = f"/instances/{instance}:start"
        self.ctx.post_proto(url)

    def stop_instance(self, instance):
        """
        Stops a single instance.

        :param str instance: A Yamcs instance name.
        """
        url = f"/instances/{instance}:stop"
        self.ctx.post_proto(url)

    def restart_instance(self, instance):
        """
        Restarts a single instance.

        :param str instance: A Yamcs instance name.
        """
        url = f"/instances/{instance}:restart"
        self.ctx.post_proto(url)

    def list_data_links(self, instance):
        """
        Deprecated. Use ``list_links(instance)``.
        """
        warnings.warn(
            "Method renamed for consistency. "
            "Use: list_links(instance) instead of list_data_links(instance)",
            FutureWarning,
        )
        return self.list_links(instance)

    def list_links(self, instance):
        """
        Lists the data links visible to this client.

        Data links are returned in random order.

        :param str instance: A Yamcs instance name.
        :rtype: ~collections.abc.Iterable[.Link]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(path="/links/" + instance)
        message = yamcsManagement_pb2.ListLinksResponse()
        message.ParseFromString(response.content)
        links = getattr(message, "links")
        return iter([Link(link) for link in links])

    def send_event(
        self,
        instance,
        message,
        event_type=None,
        time=None,
        severity="info",
        source=None,
        sequence_number=None,
    ):
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
        req = events_service_pb2.CreateEventRequest()
        req.message = message
        req.severity = severity
        if event_type:
            req.type = event_type
        if time:
            req.time.MergeFrom(to_server_time(time))
        if source:
            req.source = source
        if sequence_number is not None:
            req.sequence_number = sequence_number

        url = f"/archive/{instance}/events"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def create_link_subscription(self, instance, on_data=None, timeout=60):
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
        :rtype: .LinkSubscription
        """
        options = yamcsManagement_pb2.SubscribeLinksRequest()
        options.instance = instance
        manager = WebSocketSubscriptionManager(self.ctx, topic="links", options=options)

        # Represent subscription as a future
        subscription = LinkSubscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_link_event, subscription, on_data
        )

        manager.open(wrapped_callback)

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
        :type timeout: Optional[float]j

        :return: Future that can be used to manage the background websocket
                 subscription.
        :rtype: .TimeSubscription
        """
        options = time_service_pb2.SubscribeTimeRequest()
        options.instance = instance
        manager = WebSocketSubscriptionManager(self.ctx, topic="time", options=options)

        # Represent subscription as a future
        subscription = TimeSubscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_time_info, subscription, on_data
        )

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
        options = events_service_pb2.SubscribeEventsRequest()
        options.instance = instance
        manager = WebSocketSubscriptionManager(
            self.ctx, topic="events", options=options
        )

        # Represent subscription as a future
        subscription = WebSocketSubscriptionFuture(manager)

        wrapped_callback = functools.partial(_wrap_callback_parse_event, on_data)

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription
