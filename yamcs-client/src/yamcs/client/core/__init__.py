from __future__ import annotations

import datetime
import functools
import os
import urllib.parse
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Union,
)
from urllib.parse import urlparse

from google.protobuf import timestamp_pb2
from yamcs.client.core.auth import APIKeyCredentials, Credentials
from yamcs.client.core.context import Context
from yamcs.client.core.futures import WebSocketSubscriptionFuture
from yamcs.client.core.helpers import (
    delimit_protobuf,
    do_get,
    parse_server_time,
    to_server_time,
)
from yamcs.client.core.subscriptions import WebSocketSubscriptionManager
from yamcs.client.model import (
    AuthInfo,
    Event,
    Instance,
    InstanceTemplate,
    Link,
    LoadParameterValuesResult,
    Processor,
    RdbTablespace,
    SdlsStats,
    ServerInfo,
    Service,
    UserInfo,
)
from yamcs.client.tmtc.client import _build_value_proto
from yamcs.protobuf.archive import rocksdb_service_pb2
from yamcs.protobuf.auth import auth_pb2
from yamcs.protobuf.events import events_pb2, events_service_pb2
from yamcs.protobuf.iam import iam_pb2
from yamcs.protobuf.instances import instances_pb2, instances_service_pb2
from yamcs.protobuf.links import links_pb2
from yamcs.protobuf.processing import processing_pb2
from yamcs.protobuf.pvalue import pvalue_service_pb2
from yamcs.protobuf.sdls import sdls_pb2
from yamcs.protobuf.server import server_service_pb2
from yamcs.protobuf.services import services_service_pb2
from yamcs.protobuf.time import time_service_pb2

if TYPE_CHECKING:
    from yamcs.client.archive.client import ArchiveClient
    from yamcs.client.filetransfer.client import FileTransferClient
    from yamcs.client.links.client import LinkClient
    from yamcs.client.mdb.client import MDBClient
    from yamcs.client.storage.client import StorageClient
    from yamcs.client.tco.client import TCOClient
    from yamcs.client.timeline.client import TimelineClient
    from yamcs.client.tmtc.client import ProcessorClient
    from yamcs.client.tmtc.model import ValueUpdate

__all__ = [
    "GLOBAL_INSTANCE",
    "LinkSubscription",
    "TimeSubscription",
    "YamcsClient",
]

GLOBAL_INSTANCE = "_global"


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
    Wraps a user callback to parse Link[] updates
    from a WebSocket data message
    """
    pb = links_pb2.LinkEvent()
    message.Unpack(pb)
    links = [Link(link_pb) for link_pb in pb.links]
    subscription._process(links)
    if on_data:
        on_data(links)


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

    def get_link(self, name: str) -> Optional[Link]:
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
        Returns a snapshot of all links.
        """
        return [self._cache[k] for k in self._cache]

    def _process(self, links: List[Link]):
        for link in links:
            self._cache[link.name] = link


class YamcsClient:
    """
    Client for accessing core Yamcs resources.
    """

    def __init__(
        self,
        address: str,
        *,
        tls: bool = False,
        tls_verify: Union[bool, str] = True,
        credentials: Optional[Credentials] = None,
        user_agent: Optional[str] = None,
        keep_alive: bool = True,
        on_token_update: Optional[Callable[[Credentials], None]] = None,
    ):
        """
        :param address:
            The address of Yamcs in the format 'hostname:port'
        :param tls:
            Whether TLS encryption is expected
        :param tls_verify:
            Whether server certificate verification is
            enabled (only applicable if ``tls=True``).
            As an alternative to a boolean value, this option
            may be set to a path containing the appropriate
            TLS CA certificate bundle.
        :param credentials:
            Credentials for when the server is secured
        :param user_agent:
            Optionally override the default user agent
        :param keep_alive:
            Automatically renew the client session. If disabled,
            the session will terminate after about 30 minutes of
            inactivity.

            This property is only considered when accessing a
            server that requires authentication.
        """

        # Allow server URLs.
        # Currently undocumented, but this is expected to become the
        # default, later on.
        if address.startswith("http://") or address.startswith("https://"):
            components = urlparse(address)
            tls = components.scheme == "https"
            address = components.netloc
            address += components.path

        self.ctx = Context(
            address=address,
            tls=tls,
            credentials=credentials,
            user_agent=user_agent,
            on_token_update=on_token_update,
            tls_verify=tls_verify,
            keep_alive=keep_alive,
        )

    @staticmethod
    def from_environment():
        """
        Create a :class:`.YamcsClient`, initialized from environment variables.

        This recognizes the following environment variables:

        ``YAMCS_URL``
            Yamcs server URL

        ``YAMCS_API_KEY``
            Yamcs API key (currently only assigned to script activities)
        """
        url = os.environ["YAMCS_URL"]

        credentials = None
        api_key = os.environ.get("YAMCS_API_KEY")
        if api_key:
            credentials = APIKeyCredentials(api_key)

        return YamcsClient(url, credentials=credentials)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get_time(self, instance) -> Optional[datetime.datetime]:
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

    def get_mdb(self, instance: str) -> "MDBClient":
        """
        Return an object for working with the MDB of the specified instance.

        :param instance:
            A Yamcs instance name.
        """
        from yamcs.client.mdb.client import MDBClient

        return MDBClient(self.ctx, instance)

    def get_archive(self, instance: str) -> "ArchiveClient":
        """
        Return an object for working with the Archive of the specified instance.

        :param instance:
            A Yamcs instance name.
        """
        from yamcs.client.archive.client import ArchiveClient

        return ArchiveClient(self.ctx, instance)

    def get_file_transfer_client(self, instance: str) -> "FileTransferClient":
        """
        Return an object for working with file transfers on a specified instance.

        :param instance:
            A Yamcs instance name.
        """
        from yamcs.client.filetransfer.client import FileTransferClient

        return FileTransferClient(self.ctx, instance)

    def get_tco_client(self, instance: str, service: str) -> "TCOClient":
        """
        Return an object for Time Correlation API calls on a specified service.

        :param instance:
            A Yamcs instance name.
        :param service:
            Target service name.
        """
        from yamcs.client.tco.client import TCOClient

        return TCOClient(self.ctx, instance, service)

    def get_storage_client(self) -> "StorageClient":
        """
        Return an object for working with object storage
        """
        from yamcs.client.storage.client import StorageClient

        return StorageClient(self.ctx)

    def get_timeline_client(self, instance: str) -> "TimelineClient":
        """
        Return an object for working with Yamcs timeline items

        :param instance:
            A Yamcs instance name.
        """
        from yamcs.client.timeline.client import TimelineClient

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

    def get_processor(self, instance: str, processor: str) -> "ProcessorClient":
        """
        Return an object for working with a specific Yamcs processor.

        :param instance:
            A Yamcs instance name.
        :param processor:
            A processor name within that instance.
        """
        from yamcs.client.tmtc.client import ProcessorClient

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

    def get_link(self, instance: str, link: str) -> "LinkClient":
        """
        Return an object for working with a specific Yamcs link.

        :param instance:
            A Yamcs instance name.
        :param link:
            A link name within that instance.
        """
        from yamcs.client.links.client import LinkClient

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

    def list_rdb_tablespaces(self) -> Iterable[RdbTablespace]:
        """
        Lists RocksDB tablespaces.
        """
        response = self.ctx.get_proto(path="/archive/rocksdb/tablespaces")
        message = rocksdb_service_pb2.ListRocksDbTablespacesResponse()
        message.ParseFromString(response.content)
        tablespaces = getattr(message, "tablespaces")
        return iter([RdbTablespace(tablespace) for tablespace in tablespaces])

    def compact_rdb_column_family(
        self,
        tablespace: str,
        cf: str,
        dbpath: Optional[str] = None,
    ):
        """
        Compact a RocksDB column family.

        :param tablespace:
            RocksDB tablespace name
        :param cf:
            Column family name
        :param dbpath:
            Optional path under the tablespace root.
        """
        req = rocksdb_service_pb2.CompactDatabaseRequest()
        req.cfname = cf
        encoded_name = urllib.parse.quote_plus(dbpath or "")
        url = f"/archive/rocksdb/{tablespace}/{encoded_name}:compact"
        self.ctx.post_proto(url, data=req.SerializeToString())

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
        data: Iterator[Mapping[str, "ValueUpdate"]],
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

        def to_proto(generator: Iterator[Mapping[str, "ValueUpdate"]]):
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
        on_data: Optional[Callable[[List[Link]], None]] = None,
        timeout: float = 60,
    ) -> LinkSubscription:
        """
        Create a new subscription for receiving data link updates of an instance.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param instance:
            A Yamcs instance name.
        :param on_data:
            Function that gets called with :class:`.Link` updates. Each update
            contains state of all links.
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
        self,
        instance: str,
        on_data: Callable[[Event], None],
        filter: Optional[str] = None,
        timeout: float = 60,
    ) -> WebSocketSubscriptionFuture:
        """
        Create a new subscription for receiving events of an instance.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param instance:
            A Yamcs instance name
        :param on_data:
            Function that gets called on each :class:`.Event`.
        :param filter:
            Filter query applied to returned events. Allows for both text
            and field search.

            .. versionadded:: 1.10.1
               Compatible with Yamcs v5.10.2 onwards
        :param timeout:
            The amount of seconds to wait for the request to complete.
        :return:
            Future that can be used to manage the background websocket
            subscription.
        """
        options = events_service_pb2.SubscribeEventsRequest()
        options.instance = instance
        if filter is not None:
            options.filter = filter

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

    def sdls_get_ctr(self, instance: str, link: str, spi: int) -> int:
        response = self.ctx.get_proto(f'/sdls/{instance}/{link}/{spi}/seq')
        message = sdls_pb2.GetSeqCtrResponse()
        message.ParseFromString(response.content)
        return message.seq

    def sdls_reset_ctr(self, instance: str, link: str, spi: int):
        self.ctx.delete_proto(f'/sdls/{instance}/{link}/{spi}/seq')

    def sdls_get_stats(self, instance: str) -> Iterable[SdlsStats]:
        response = self.ctx.get_proto(f'/sdls/{instance}/stats')
        message = sdls_pb2.GetStatsResponse()
        message.ParseFromString(response.content)
        stats = getattr(message, 'stats')
        return iter([SdlsStats(stat) for stat in stats])

    def sdls_set_key(self, instance: str, link: str, spi: int, key: bytes):
        self.ctx.put_proto(f'/sdls/{instance}/{link}/{spi}/key', data=key)

    def close(self):
        """Close this client session"""
        self.ctx.close()
