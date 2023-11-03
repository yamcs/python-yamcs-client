import datetime
import functools
from typing import Any, Callable, Iterable, Iterator, List, Mapping, Optional

from google.protobuf import timestamp_pb2
from yamcs.archive.client import ArchiveClient
from yamcs.core.context import Context
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.helpers import (
    delimit_protobuf,
    do_get,
    parse_server_time,
    to_server_time,
)
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
    LoadParameterValuesResult,
    Processor,
    ServerInfo,
    Service,
    UserInfo,
)
from yamcs.protobuf.auth import auth_pb2
from yamcs.protobuf.events import events_pb2, events_service_pb2
from yamcs.protobuf.iam import iam_pb2
from yamcs.protobuf.instances import instances_pb2, instances_service_pb2
from yamcs.protobuf.links import links_pb2
from yamcs.protobuf.processing import processing_pb2
from yamcs.protobuf.pvalue import pvalue_service_pb2
from yamcs.protobuf.server import server_service_pb2
from yamcs.protobuf.services import services_service_pb2
from yamcs.protobuf.time import time_service_pb2
from yamcs.storage.client import StorageClient
from yamcs.tco.client import TCOClient
from yamcs.timeline.client import TimelineClient
from yamcs.tmtc.client import ProcessorClient, _build_value_proto
from yamcs.tmtc.model import ValueUpdate


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
    pb = events_pb2.Event()
    message.Unpack(pb)
    event = Event(pb)
    on_data(event)


def _wrap_callback_parse_link_event(subscription, on_data, message):
    """
    Wraps a user callback to parse LinkEvents
    from a WebSocket data message
    """
    pb = links_pb2.LinkEvent()
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

        self.time: Optional[datetime.datetime] = None
        """The last time info."""

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

    def get_link(self, name: str) -> Link:
        """
        Returns the latest link state.

        :param name:
            Identifying name of the data link
        """
        if name in self._cache:
            return self._cache[name]
        return None

    def list_links(self) -> List[Link]:
        """
        Returns a snapshot of all instance links.
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

    def __init__(self, address: str, **kwargs):
        """
        :param address:
            The address of Yamcs in the format 'hostname:port'
        :param bool tls:
            Whether TLS encryption is expected
        :param tls_verify:
            Whether server certificate verification is
            enabled (only applicable if ``tls=True``).
            As an alternative to a boolean value, this option
            may be set to a path containing the appropriate
            TLS CA certificate bundle.
        :type tls_verify:
            Optional[Union[bool, str]]
        :param Optional[.Credentials] credentials:
            Credentials for when the server is secured
        :param Optional[str] user_agent:
            Optionally override the default user agent
        """
        self.ctx = Context(address, **kwargs)

    def get_time(self, instance) -> datetime.datetime:
        """
        Return the current mission time for the specified instance.
        """
        url = f"/instances/{instance}"
        response = self.ctx.get_proto(url)
        message = instances_pb2.YamcsInstance()
        message.ParseFromString(response.content)
        if message.HasField("missionTime"):
            return parse_server_time(message.missionTime)
        return None

    def get_server_info(self) -> ServerInfo:
        """
        Return general server info.
        """
        response = self.ctx.get_proto(path="")
        message = server_service_pb2.GetServerInfoResponse()
        message.ParseFromString(response.content)
        return ServerInfo(message)

    def get_auth_info(self) -> AuthInfo:
        """
        Returns general authentication information. This operation
        does not require authenticating and is useful to test
        if a server requires authentication or not.
        """
        response = do_get(
            self.ctx.session,
            self.ctx.auth_root,  # Full URL, so don't use get_proto
            headers={"Accept": "application/protobuf"},
        )
        message = auth_pb2.AuthInfo()
        message.ParseFromString(response.content)
        return AuthInfo(message)

    def get_user_info(self) -> UserInfo:
        """
        Get information on the authenticated user.
        """
        response = self.ctx.get_proto(path="/user")
        message = iam_pb2.UserInfo()
        message.ParseFromString(response.content)
        return UserInfo(message)

    def get_mdb(self, instance: str) -> MDBClient:
        """
        Return an object for working with the MDB of the specified instance.

        :param instance:
            A Yamcs instance name.
        """
        return MDBClient(self.ctx, instance)

    def get_archive(self, instance: str) -> ArchiveClient:
        """
        Return an object for working with the Archive of the specified instance.

        :param instance:
            A Yamcs instance name.
        """
        return ArchiveClient(self.ctx, instance)

    def get_file_transfer_client(self, instance: str) -> FileTransferClient:
        """
        Return an object for working with file transfers on a specified instance.

        :param instance:
            A Yamcs instance name.
        """
        return FileTransferClient(self.ctx, instance)

    def get_tco_client(self, instance: str, service: str) -> TCOClient:
        """
        Return an object for Time Correlation API calls on a specified service.

        :param instance:
            A Yamcs instance name.
        :param service:
            Target service name.
        """
        return TCOClient(self.ctx, instance, service)

    def get_storage_client(self, instance: str = "_global") -> StorageClient:
        """
        Return an object for working with object storage

        :param instance:
            The storage instance.
        """
        return StorageClient(self.ctx, instance)

    def get_timeline_client(self, instance: str) -> TimelineClient:
        """
        Return an object for working with Yamcs timeline items

        :param instance:
            A Yamcs instance name.
        """
        return TimelineClient(self.ctx, instance)

    def create_instance(
        self,
        name: str,
        template: str,
        args: Optional[Mapping[str, Any]] = None,
        labels: Optional[Mapping[str, str]] = None,
    ):
        """
        Create a new instance based on an existing template. This method blocks
        until the instance is fully started.

        :param instance:
            A Yamcs instance name.
        :param template:
            The name of an existing template.
        """
        req = instances_service_pb2.CreateInstanceRequest()
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

    def list_instance_templates(self) -> Iterable[InstanceTemplate]:
        """
        List the available instance templates.
        """
        response = self.ctx.get_proto(path="/instance-templates")
        message = instances_service_pb2.ListInstanceTemplatesResponse()
        message.ParseFromString(response.content)
        templates = getattr(message, "templates")
        return iter([InstanceTemplate(template) for template in templates])

    def list_services(self, instance: str) -> Iterable[Service]:
        """
        List the services for an instance.

        :param instance:
            A Yamcs instance name.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        url = f"/services/{instance}"
        response = self.ctx.get_proto(path=url)
        message = services_service_pb2.ListServicesResponse()
        message.ParseFromString(response.content)
        services = getattr(message, "services")
        return iter([Service(service) for service in services])

    def start_service(self, instance: str, service: str):
        """
        Starts a single service.

        :param instance:
            A Yamcs instance name.
        :param service:
            The name of the service.
        """
        url = f"/services/{instance}/{service}:start"
        self.ctx.post_proto(url)

    def stop_service(self, instance: str, service: str):
        """
        Stops a single service.

        :param instance:
            A Yamcs instance name.
        :param service:
            The name of the service.
        """
        url = f"/services/{instance}/{service}:stop"
        self.ctx.post_proto(url)

    def list_processors(self, instance: Optional[str] = None) -> Iterable[Processor]:
        """
        Lists the processors.

        Processors are returned in lexicographical order.

        :param instance:
            A Yamcs instance name.
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

    def get_processor(self, instance: str, processor: str) -> ProcessorClient:
        """
        Return an object for working with a specific Yamcs processor.

        :param instance:
            A Yamcs instance name.
        :param processor:
            A processor name within that instance.
        """
        return ProcessorClient(self.ctx, instance, processor)

    def delete_processor(self, instance: str, processor: str):
        """
        Delete a processor.

        :param instance:
            A Yamcs instance name.
        :param processor:
            A processor name within that instance.
        """
        url = f"/processors/{instance}/{processor}"
        self.ctx.delete_proto(url)

    def get_link(self, instance: str, link: str) -> LinkClient:
        """
        Return an object for working with a specific Yamcs link.

        :param instance:
            A Yamcs instance name.
        :param link:
            A link name within that instance.
        """
        return LinkClient(self.ctx, instance, link)

    def list_instances(self) -> Iterable[Instance]:
        """
        Lists the instances.

        Instances are returned in lexicographical order.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(path="/instances")
        message = instances_service_pb2.ListInstancesResponse()
        message.ParseFromString(response.content)
        instances = getattr(message, "instances")
        return iter([Instance(instance) for instance in instances])

    def start_instance(self, instance: str):
        """
        Starts a single instance.

        :param instance:
            A Yamcs instance name.
        """
        url = f"/instances/{instance}:start"
        self.ctx.post_proto(url)

    def stop_instance(self, instance: str):
        """
        Stops a single instance.

        :param instance:
            A Yamcs instance name.
        """
        url = f"/instances/{instance}:stop"
        self.ctx.post_proto(url)

    def restart_instance(self, instance: str):
        """
        Restarts a single instance.

        :param instance:
            A Yamcs instance name.
        """
        url = f"/instances/{instance}:restart"
        self.ctx.post_proto(url)

    def list_links(self, instance: str) -> Iterable[Link]:
        """
        Lists the data links visible to this client.

        Data links are returned in random order.

        :param instance:
            A Yamcs instance name.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(path="/links/" + instance)
        message = links_pb2.ListLinksResponse()
        message.ParseFromString(response.content)
        links = getattr(message, "links")
        return iter([Link(link) for link in links])

    def send_event(
        self,
        instance: str,
        message: str,
        event_type: Optional[str] = None,
        time: Optional[datetime.datetime] = None,
        severity: Optional[str] = "info",
        source: Optional[str] = None,
        sequence_number: Optional[int] = None,
        extra: Optional[Mapping[str, str]] = None,
    ):
        """
        Post a new event.

        :param instance:
            A Yamcs instance name.
        :param message:
            Event message.
        :param event_type:
            Type of event.

        :param severity:
            The severity level of the event. One of ``info``,
            ``watch``, ``warning``, ``distress``, ``critical``
            or ``severe``. Defaults to ``info``.
        :param time:
            Time of the event. If unspecified, defaults to mission time.
        :param source:
            Source of the event. Useful for grouping events in the
            archive. When unset this defaults to ``User``.
        :param event_type:
            Event type.
        :param sequence_number:
            Sequence number of this event. This is used to
            determine unicity of events at the same time and
            coming from the same source. If not set Yamcs
            will automatically assign a sequential number as
            if every submitted event is unique.
        :param extra:
            Extra event properties.

            .. versionadded:: 1.8.4
               Compatible with Yamcs 5.7.3 onwards
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
            req.sequenceNumber = sequence_number
        if extra:
            for key in extra:
                req.extra[key] = extra[key]

        url = f"/archive/{instance}/events"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def load_parameter_values(
        self,
        instance: str,
        data: Iterator[Mapping[str, ValueUpdate]],
        stream: str = "pp_dump",
        chunk_size: int = 32 * 1024,
    ) -> LoadParameterValuesResult:
        """
        Load an indefinite amount of parameter values into Yamcs.

        .. versionadded:: 1.9.1
           Compatible with Yamcs 5.8.8 onwards

        :param instance:
            Yamcs instance name
        :param data:
            Generator that yields batches of parameter values,
            keyed by parameter name.
        :param stream:
            Stream where to send the parameters to.
        :param chunk_size:
            HTTP chunk size. Multiple updates are grouped in chunks
            of about this size.
        """

        def to_proto(generator: Iterator[Mapping[str, ValueUpdate]]):
            for values in generator:
                proto = pvalue_service_pb2.LoadParameterValuesRequest()
                for key in values:
                    value_update = values[key]
                    item = proto.values.add()
                    item.parameter = key
                    item.value.MergeFrom(_build_value_proto(value_update.value))
                    if value_update.generation_time:
                        item.generationTime.MergeFrom(
                            to_server_time(value_update.generation_time)
                        )
                    if value_update.expires_in is not None:
                        item.expiresIn = int(value_update.expires_in * 1000)

                yield proto

        generator = delimit_protobuf(to_proto(data), chunk_size=chunk_size)

        url = f"/parameter-values/{instance}/streams/{stream}:load"
        response = self.ctx.post_proto(url, data=generator)
        message = pvalue_service_pb2.LoadParameterValuesResponse()
        message.ParseFromString(response.content)
        return LoadParameterValuesResult(message)

    def create_link_subscription(
        self,
        instance: str,
        on_data: Optional[Callable[[LinkEvent], None]] = None,
        timeout: float = 60,
    ) -> LinkSubscription:
        """
        Create a new subscription for receiving data link updates of an instance.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param instance:
            A Yamcs instance name.
        :param on_data:
            Function that gets called with :class:`.LinkEvent` updates.
        :param timeout:
            The amount of seconds to wait for the request to complete.
        :return:
            Future that can be used to manage the background websocket
            subscription.
        """
        options = links_pb2.SubscribeLinksRequest()
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

    def create_time_subscription(
        self,
        instance: str,
        on_data: Optional[Callable[[datetime.datetime], None]] = None,
        timeout: float = 60,
    ) -> TimeSubscription:
        """
        Create a new subscription for receiving time updates of an instance.
        Time updates are emitted at 1Hz.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param instance:
            A Yamcs instance name
        :param on_data:
            Function that gets called with :class:`~datetime.datetime` updates.
        :param timeout:
            The amount of seconds to wait for the request to complete.

        :return:
            Future that can be used to manage the background websocket
            subscription.
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

    def create_event_subscription(
        self, instance: str, on_data: Callable[[Event], None], timeout: float = 60
    ) -> WebSocketSubscriptionFuture:
        """
        Create a new subscription for receiving events of an instance.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param instance:
            A Yamcs instance name
        :param on_data:
            Function that gets called on each :class:`.Event`.
        :param timeout:
            The amount of seconds to wait for the request to complete.
        :return:
            Future that can be used to manage the background websocket
            subscription.
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
