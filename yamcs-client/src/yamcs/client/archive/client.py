import functools
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

from yamcs.client.archive.model import (
    IndexGroup,
    ParameterRange,
    ResultSet,
    Sample,
    Stream,
    StreamData,
    Table,
)
from yamcs.client.core import pagination
from yamcs.client.core.context import Context
from yamcs.client.core.exceptions import YamcsError
from yamcs.client.core.futures import WebSocketSubscriptionFuture
from yamcs.client.core.helpers import (
    split_protobuf_stream,
    to_isostring,
    to_named_object_ids,
    to_server_time,
)
from yamcs.client.core.subscriptions import WebSocketSubscriptionManager
from yamcs.client.model import Event
from yamcs.client.tmtc.model import (
    Alarm,
    CommandHistory,
    EventAlarm,
    Packet,
    ParameterAlarm,
    ParameterData,
    ParameterValue,
)
from yamcs.protobuf.alarms import alarms_pb2, alarms_service_pb2
from yamcs.protobuf.archive import (
    archive_pb2,
    index_service_pb2,
    parameter_archive_service_pb2,
)
from yamcs.protobuf.commanding import commanding_pb2, commands_service_pb2
from yamcs.protobuf.events import events_pb2, events_service_pb2
from yamcs.protobuf.packets import packets_pb2, packets_service_pb2
from yamcs.protobuf.pvalue import pvalue_pb2
from yamcs.protobuf.table import table_pb2

__all__ = [
    "ArchiveClient",
]


def _wrap_callback_parse_stream_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse StreamData
    from a WebSocket data message
    """
    pb = table_pb2.StreamData()
    message.Unpack(pb)
    on_data(StreamData(pb))


class ArchiveClient:
    def __init__(self, ctx: Context, instance: str):
        super(ArchiveClient, self).__init__()
        self.ctx = ctx
        self._instance = instance

    def list_packet_names(self) -> Iterable[str]:
        """
        Returns the existing packet names.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = f"/archive/{self._instance}/packet-names"
        response = self.ctx.get_proto(path=path)
        message = packets_service_pb2.ListPacketNamesResponse()
        message.ParseFromString(response.content)
        names = getattr(message, "name")
        return iter(names)

    def list_packet_histogram(
        self,
        name: Optional[str] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        merge_time: float = 2,
    ) -> Iterable[IndexGroup]:
        """
        Reads packet-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param merge_time:
            Maximum gap in seconds before two consecutive index
            records are merged together.
        """
        params = {}
        if name is not None:
            params["name"] = name
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)
        if merge_time is not None:
            params["mergeTime"] = int(merge_time * 1000)

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/packet-index",
            params=params,
            response_class=index_service_pb2.IndexResponse,
            items_key="group",
            item_mapper=IndexGroup,
        )

    def list_processed_parameter_groups(self) -> Iterable[str]:
        """
        Returns the existing parameter groups.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = f"/archive/{self._instance}/parameter-groups"
        response = self.ctx.get_proto(path=path)
        message = archive_pb2.ParameterGroupInfo()
        message.ParseFromString(response.content)
        groups = getattr(message, "groups")
        return iter(groups)

    def list_processed_parameter_group_histogram(
        self,
        group: Optional[str] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        merge_time: float = 20,
    ) -> Iterable[IndexGroup]:
        """
        Reads index records related to processed parameter groups between the
        specified start and stop time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param merge_time:
            Maximum gap in seconds before two consecutive index
            records are merged together.
        """
        params = {}
        if group is not None:
            params["group"] = group
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)
        if merge_time is not None:
            params["mergeTime"] = int(merge_time * 1000)

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/parameter-index",
            params=params,
            response_class=index_service_pb2.IndexResponse,
            items_key="group",
            item_mapper=IndexGroup,
        )

    def list_event_sources(self) -> Iterable[str]:
        """
        Returns the existing event sources.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = f"/archive/{self._instance}/events/sources"
        response = self.ctx.get_proto(path=path)
        message = events_service_pb2.ListEventSourcesResponse()
        message.ParseFromString(response.content)
        sources = getattr(message, "source")
        return iter(sources)

    def list_event_histogram(
        self,
        source: Optional[str] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        merge_time: float = 2,
    ) -> Iterable[IndexGroup]:
        """
        Reads event-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param merge_time:
            Maximum gap in seconds before two consecutive index
            records are merged together.
        """
        params = {}
        if source is not None:
            params["source"] = source
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)
        if merge_time is not None:
            params["mergeTime"] = int(merge_time * 1000)

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/event-index",
            params=params,
            response_class=index_service_pb2.IndexResponse,
            items_key="group",
            item_mapper=IndexGroup,
        )

    def list_command_histogram(
        self,
        name: Optional[str] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        merge_time: float = 2,
    ) -> Iterable[IndexGroup]:
        """
        Reads command-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param merge_time:
            Maximum gap in seconds before two consecutive index
            records are merged together.
        """
        params = {}
        if name is not None:
            params["name"] = name
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)
        if merge_time is not None:
            params["mergeTime"] = int(merge_time * 1000)

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/command-index",
            params=params,
            response_class=index_service_pb2.IndexResponse,
            items_key="group",
            item_mapper=IndexGroup,
        )

    def list_completeness_index(
        self,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        merge_time: float = 2,
    ) -> Iterable[IndexGroup]:
        """
        Reads completeness index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param merge_time:
            Maximum gap in seconds before two consecutive index
            records are merged together.
        """
        params = {}
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)
        if merge_time is not None:
            params["mergeTime"] = int(merge_time * 1000)

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/completeness-index",
            params=params,
            response_class=index_service_pb2.IndexResponse,
            items_key="group",
            item_mapper=IndexGroup,
        )

    def list_alarms(
        self,
        name: Optional[str] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        page_size: int = 500,
        descending: bool = False,
    ) -> Iterable[Alarm]:
        """
        Reads alarm information between the specified start and stop time.

        Alarms are sorted by trigger time, name and sequence number.

        :param name:
            Filter by alarm name
        :param start:
            Minimum trigger time (inclusive)
        :param stop:
            Maximum trigger time (exclusive)
        :param page_size:
            Page size of underlying requests. Higher values imply
            less overhead, but risk hitting the maximum message size
            limit.
        :param descending:
            If set to ``True`` alarms are fetched in reverse
            order (most recent first).
        """
        params: Dict[str, Any] = {
            "order": "desc" if descending else "asc",
        }
        if name is not None:
            params["name"] = name
        if page_size is not None:
            params["limit"] = page_size
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)

        def to_alarm(proto):
            if proto.type == alarms_pb2.PARAMETER:
                return ParameterAlarm(proto)
            elif proto.type == alarms_pb2.EVENT:
                return EventAlarm(proto)
            else:
                raise YamcsError("Unexpected type " + str(proto.type))

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/alarms",
            params=params,
            response_class=alarms_service_pb2.ListAlarmsResponse,
            items_key="alarms",
            item_mapper=to_alarm,
        )

    def list_packets(
        self,
        name: Optional[str] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        page_size: int = 500,
        descending: bool = False,
    ) -> Iterable[Packet]:
        """
        Reads packet information between the specified start and stop
        time.

        Packets are sorted by generation time and sequence number.

        .. note::

            This method will send out multiple requests when more than
            ``page_size`` packets are queried. For large queries, consider
            using :meth:`stream_packets` instead, it uses server-streaming
            based on a single request.

        :param name:
            Archived name of the packet
        :param start:
            Minimum generation time of the returned packets (inclusive)
        :param stop:
            Maximum generation time of the returned packets (exclusive)
        :param page_size:
            Page size of underlying requests. Higher values imply
            less overhead, but risk hitting the maximum message size
            limit.
        :param descending:
            If set to ``True`` packets are fetched in reverse
            order (most recent first).
        """
        params: Dict[str, Any] = {
            "order": "desc" if descending else "asc",
        }
        if name is not None:
            params["name"] = name
        if page_size is not None:
            params["limit"] = page_size
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/packets",
            params=params,
            response_class=packets_service_pb2.ListPacketsResponse,
            items_key="packet",
            item_mapper=Packet,
        )

    def stream_packets(
        self,
        name: Optional[Union[str, List[str]]] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        chunk_size: int = 32 * 1024,
    ) -> Iterable[Packet]:
        """
        Reads packet information between the specified start and stop time.

        .. versionadded:: 1.9.1

        :param name:
            If specified, return only packets with this archived name.
        :param start:
            Minimum generation time of the returned packets (inclusive)
        :param stop:
            Maximum generation time of the returned packets (exclusive)
        """
        options = packets_service_pb2.StreamPacketsRequest()
        if name is not None:
            if isinstance(name, str):
                options.name.extend([name])
            else:
                options.name.extend(name)
        if start is not None:
            options.start.MergeFrom(to_server_time(start))
        if stop is not None:
            options.stop.MergeFrom(to_server_time(stop))

        def generate():
            path = f"/stream-archive/{self._instance}:streamPackets"
            response = self.ctx.post_proto(
                path=path, data=options.SerializeToString(), stream=True
            )
            for message in split_protobuf_stream(
                response.iter_content(chunk_size=chunk_size), packets_pb2.TmPacketData
            ):
                yield Packet(message)

        return generate()

    def get_packet(
        self,
        generation_time: datetime,
        sequence_number: int,
        partition: Optional[str] = None,
    ) -> Packet:
        """
        Gets a single packet by its identifying key (partition, gentime, seqNum).

        :param generation_time:
            When the packet was generated (packet time)
        :param sequence_number:
            Sequence number of the packet
        :param partition:
            Packet partition name. This property works only against recent versions
            of Yamcs,and will become required in the future (it was erroneously
            omitted).
        """
        url = f"/archive/{self._instance}/packets/"

        # Currently we allow the partition to be unspecified, but this should
        # become deprecated within a few more Yamcs versions.
        # (this endpoint variation was only recently introduced)
        if partition:
            url += urllib.parse.quote_plus(partition) + "/"
        url += f"{to_isostring(generation_time)}/{sequence_number}"
        response = self.ctx.get_proto(url)
        message = packets_pb2.TmPacketData()
        message.ParseFromString(response.content)
        return Packet(message)

    def export_parameter_values(
        self,
        parameters: List[str],
        namespace: Optional[str],
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        interval: Optional[float] = None,
        chunk_size: int = 32 * 1024,
    ) -> Iterable:
        """
        Export parameter values in CSV format.

        .. versionadded:: 1.9.1

        :param parameters:
            List of parameter names. These may be
            fully-qualified XTCE name or an alias
            in the format ``NAMESPACE/NAME``.
        :param namespace:
            Preferred namespace of the names in the returned CSV header
        :param start:
            Minimum generation time of the returned values (inclusive)
        :param stop:
            Maximum generation time of the returned values (exclusive)
        :param interval:
            If specified, only one value for each interval is returned. The interval is
            expressed in seconds.
        :return:
            An iterator over received chunks
        """
        params: Dict[str, Any] = {"parameters": parameters}
        if namespace is not None:
            params["namespace"] = namespace
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)
        if interval is not None:
            params["interval"] = int(interval * 1000)

        path = f"/archive/{self._instance}:exportParameterValues"
        response = self.ctx.get_proto(path=path, params=params, stream=True)
        return response.iter_content(chunk_size=chunk_size)

    def export_commands(
        self,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        chunk_size: int = 32 * 1024,
    ) -> Iterable:
        """
        Export command history.

        Commands are sorted by generation time, origin and sequence number.

        :param start:
            Minimum generation time of the returned commands (inclusive)
        :param stop:
            Maximum generation time of the returned commands (exclusive)
        :return:
            An iterator over received chunks
        """
        params = {}
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)

        path = f"/archive/{self._instance}:exportCommands"
        response = self.ctx.get_proto(path=path, params=params, stream=True)
        return response.iter_content(chunk_size=chunk_size)

    def export_packets(
        self,
        name: Optional[str] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        chunk_size: int = 32 * 1024,
    ) -> Iterable:
        """
        Export raw packets.

        Packets are sorted by generation time and sequence number.

        :param name:
            Archived name of the packet
        :param start:
            Minimum generation time of the returned packets (inclusive)
        :param stop:
            Maximum generation time of the returned packets (exclusive)
        :return:
            An iterator over received chunks
        """
        params = {}
        if name is not None:
            params["name"] = name
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)

        path = f"/archive/{self._instance}:exportPackets"
        response = self.ctx.get_proto(path=path, params=params, stream=True)
        return response.iter_content(chunk_size=chunk_size)

    def list_events(
        self,
        source: Optional[str] = None,
        severity: Optional[str] = None,
        text_filter: Optional[str] = None,
        filter: Optional[str] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        page_size: int = 500,
        descending: bool = False,
    ) -> Iterable[Event]:
        """
        Reads events between the specified start and stop time.

        Events are sorted by generation time, source, then sequence number.

        .. note::

            This method will send out multiple requests when more than
            ``page_size`` events are queried. For large queries, consider
            using :meth:`stream_events` instead, it uses server-streaming
            based on a single request.

        :param source:
            The source of the returned events.
        :param severity:
            The minimum severity level of the returned events.
            One of ``INFO``, ``WATCH``, ``WARNING``, ``DISTRESS``,
            ``CRITICAL`` or ``SEVERE``.
        :param text_filter:
            Filter the text message of the returned events
        :param filter:
            Filter query, allows for both text and field search.

            .. versionadded:: 1.10.1
               Compatible with Yamcs v5.10.2 onwards
        :param start:
            Minimum start date of the returned events (inclusive)
        :param stop:
            Maximum start date of the returned events (exclusive)
        :param page_size:
            Page size of underlying requests. Higher values imply
            less overhead, but risk hitting the maximum message size
            limit.
        :param descending:
            If set to ``True`` events are fetched in reverse
            order (most recent first).
        """
        params: Dict[str, Any] = {
            "order": "desc" if descending else "asc",
        }
        if source is not None:
            params["source"] = source
        if page_size is not None:
            params["limit"] = page_size
        if severity is not None:
            params["severity"] = severity
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)
        if text_filter is not None:
            params["q"] = text_filter
        if filter is not None:
            params["filter"] = filter

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/events",
            params=params,
            response_class=events_service_pb2.ListEventsResponse,
            items_key="event",
            item_mapper=Event,
        )

    def stream_events(
        self,
        source: Optional[Union[str, List[str]]] = None,
        severity: Optional[str] = None,
        text_filter: Optional[str] = None,
        filter: Optional[str] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        chunk_size: int = 32 * 1024,
    ) -> Iterable[Event]:
        """
        Reads events between the specified start and stop time.

        .. versionadded:: 1.9.1

        :param source:
            If specified, return only events with this source.
        :param severity:
            The minimum severity level of the returned events.
            One of ``INFO``, ``WATCH``, ``WARNING``, ``DISTRESS``,
            ``CRITICAL`` or ``SEVERE``.
        :param text_filter:
            Filter the text message of the returned events
        :param filter:
            Filter query applied to returned events. Allows for both text
            and field search.

            .. versionadded:: 1.10.1
               Compatible with Yamcs v5.10.2 onwards
        :param start:
            Minimum generation time of the returned events (inclusive)
        :param stop:
            Maximum generation time of the returned events (exclusive)
        """
        options = events_service_pb2.StreamEventsRequest()
        if source is not None:
            if isinstance(source, str):
                options.source.extend([source])
            else:
                options.source.extend(source)
        if severity is not None:
            options.severity = severity
        if start is not None:
            options.start.MergeFrom(to_server_time(start))
        if stop is not None:
            options.stop.MergeFrom(to_server_time(stop))
        if text_filter is not None:
            options.q = text_filter
        if filter is not None:
            options.filter = filter

        def generate():
            path = f"/stream-archive/{self._instance}:streamEvents"
            response = self.ctx.post_proto(
                path=path, data=options.SerializeToString(), stream=True
            )
            for message in split_protobuf_stream(
                response.iter_content(chunk_size=chunk_size), events_pb2.Event
            ):
                yield Event(message)

        return generate()

    def sample_parameter_values(
        self,
        parameter: str,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        sample_count: int = 500,
        parameter_cache: str = "realtime",
        source: str = "ParameterArchive",
    ) -> List[Sample]:
        """
        Returns parameter samples.

        The query range is split in sample intervals of equal length. For
        each interval a :class:`.Sample` is returned which describes the
        min, max, count and avg during that interval.

        Note that sample times are determined without considering the
        actual parameter values. Two separate queries with equal start/stop
        arguments will always return the same number of samples with the
        same timestamps. This is done to ease merging of multiple sample
        series. You should always be explicit about the ``start`` and ``stop``
        times when relying on this property.

        :param parameter:
            Either a fully-qualified XTCE name or an alias in the
            format ``NAMESPACE/NAME``.
        :param start:
            Minimum generation time of the sampled
            parameter values (inclusive). If not set
            this defaults to one hour ago.
        :param stop:
            Maximum generation time of the sampled
            parameter values (exclusive). If not set
            this defaults to the current time.
        :param sample_count:
            The number of returned samples.
        :param parameter_cache:
            Specify the name of the processor who's
            parameter cache is merged with already
            archived values. To disable results from
            the parameter cache, set this to ``None``.
        :param source:
            Specify how to retrieve parameter values. By
            default this uses the ``ParameterArchive`` which
            is optimized for retrieval. For Yamcs instances
            that do not enable the ``ParameterArchive``, you can
            still get results by specifying ``replay`` as the
            source. Replay requests take longer to return because
            the data needs to be reprocessed.
        """
        path = f"/archive/{self._instance}/parameters{parameter}/samples"
        now = datetime.now(tz=timezone.utc)
        params = {
            "count": sample_count,
            "source": source,
            "start": to_isostring(now - timedelta(hours=1)),
            "stop": to_isostring(now),
        }
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)

        if parameter_cache:
            params["processor"] = parameter_cache
        else:
            params["norealtime"] = True

        response = self.ctx.get_proto(path=path, params=params)
        message = pvalue_pb2.TimeSeries()
        message.ParseFromString(response.content)
        samples = getattr(message, "sample")
        return [Sample(s) for s in samples]

    def list_parameter_ranges(
        self,
        parameter: str,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        min_gap: Optional[float] = None,
        max_gap: Optional[float] = None,
        min_range: Optional[float] = None,
        max_values: int = 100,
        parameter_cache: str = "realtime",
    ) -> List[ParameterRange]:
        """
        Returns parameter ranges between the specified start and stop time.

        Each range indicates an interval during which this parameter's
        value was uninterrupted and unchanged.

        Ranges are a good fit for retrieving the value of a parameter
        that does not change frequently. For example an on/off indicator
        or some operational status. Querying ranges will then induce
        much less overhead than manually processing the output of
        :meth:`list_parameter_values` would.

        The maximum number of returned ranges is limited to 500.

        :param parameter:
            Either a fully-qualified XTCE name or an alias in the
            format ``NAMESPACE/NAME``.
        :param start:
            Minimum generation time of the considered values (inclusive)
        :param stop:
            Maximum generation time of the considered values (exclusive)
        :param min_gap:
            Time in seconds. Any gap (detected based on parameter
            expiration) smaller than this will be ignored.
            However if the parameter changes value, the ranges
            will still be split.
        :param max_gap:
            Time in seconds. If the distance between two
            subsequent parameter values is bigger than
            this value (but smaller than the parameter
            expiration), then an artificial gap is
            created. This also applies if there is no
            expiration defined for the parameter.
        :param min_range:
            Time in seconds. Minimum duration of returned
            ranges. If multiple values occur within the
            range, the most frequent can be accessed using
            the ``entries`` property.
        :param max_values:
            Maximum number of unique values, tallied across the
            full requested range. Use this in combination with
            ``min_range`` to further optimize for transfer size.
            This value is limited to 100 at most.
        :param parameter_cache:
            Specify the name of the processor who's
            parameter cache is merged with already
            archived values. To disable results from
            the parameter cache, set this to ``None``.
        """
        path = f"/archive/{self._instance}/parameters{parameter}/ranges"
        params = {}
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)
        if min_gap is not None:
            params["minGap"] = int(min_gap * 1000)
        if max_gap is not None:
            params["maxGap"] = int(max_gap * 1000)
        if min_range is not None:
            params["minRange"] = int(min_range * 1000)
        if max_values is not None:
            params["maxValues"] = max_values

        if parameter_cache:
            params["processor"] = parameter_cache
        else:
            params["norealtime"] = True

        response = self.ctx.get_proto(path=path, params=params)
        message = pvalue_pb2.Ranges()
        message.ParseFromString(response.content)
        ranges = getattr(message, "range")
        return [ParameterRange(r) for r in ranges]

    def list_parameter_values(
        self,
        parameter: str,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        page_size: int = 500,
        descending: bool = False,
        parameter_cache: str = "realtime",
        source: str = "ParameterArchive",
    ) -> Iterable[ParameterValue]:
        """
        Reads parameter values between the specified start and stop time.

        .. note::

            This method will send out multiple requests when more than
            ``page_size`` values are queried. For large queries, consider
            using :meth:`stream_parameter_values` instead, it uses server-streaming
            based on a single request, and supports downloading the values of
            multiple parameter at the same time.

        :param parameter:
            Either a fully-qualified XTCE name or an alias in the
            format ``NAMESPACE/NAME``.
        :param start:
            Minimum generation time of the returned values (inclusive)
        :param stop:
            Maximum generation time of the returned values (exclusive)
        :param page_size:
            Page size of underlying requests. Higher values imply
            less overhead, but risk hitting the maximum message size
            limit.
        :param descending:
            If set to ``True`` values are fetched in reverse
            order (most recent first).
        :param parameter_cache:
            Specify the name of the processor who's
            parameter cache is merged with already
            archived values. To disable results from
            the parameter cache, set this to ``None``.
        :param source:
            Specify how to retrieve parameter values. By
            default this uses the ``ParameterArchive`` which
            is optimized for retrieval. For Yamcs instances
            that do not enable the ``ParameterArchive``, you can
            still get results by specifying ``replay`` as the
            source. Replay requests take longer to return because
            the data needs to be reprocessed.
        """
        params: Dict[str, Any] = {
            "source": source,
            "order": "desc" if descending else "asc",
        }
        if page_size is not None:
            params["limit"] = page_size
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)

        if parameter_cache:
            params["processor"] = parameter_cache
        else:
            params["norealtime"] = True

        encoded_name = urllib.parse.quote_plus(parameter)
        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/parameters/{encoded_name}",
            params=params,
            response_class=archive_pb2.ListParameterHistoryResponse,
            items_key="parameter",
            item_mapper=ParameterValue,
        )

    def stream_parameter_values(
        self,
        parameters: Union[str, List[str]],
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        tm_links: Optional[Union[str, List[str]]] = None,
        chunk_size: int = 32 * 1024,
    ) -> Iterable[ParameterData]:
        """
        Reads parameter values between the specified start and stop time.

        Value updates are emitted for each unique generation time within
        the queried range. If one of the parameters does not have a value
        for a specific generation time, it is not included in the update.

        :param parameters:
            Parameter(s) to be queried.
        :param start:
            Minimum generation time of the returned values (inclusive)
        :param stop:
            Maximum generation time of the returned values (exclusive)
        :param tm_links:
            If set, include only values that were received through
            a specific link.

            .. versionadded:: 1.8.4
               Compatible with Yamcs 5.7.4 onwards
        """
        options = archive_pb2.StreamParameterValuesRequest()
        options.ids.extend(to_named_object_ids(parameters))
        if start is not None:
            options.start.MergeFrom(to_server_time(start))
        if stop is not None:
            options.stop.MergeFrom(to_server_time(stop))
        if tm_links:
            if isinstance(tm_links, str):
                options.tmLinks.extend([tm_links])
            else:
                options.tmLinks.extend(tm_links)

        def generate():
            path = f"/stream-archive/{self._instance}:streamParameterValues"
            response = self.ctx.post_proto(
                path=path, data=options.SerializeToString(), stream=True
            )
            for message in split_protobuf_stream(
                response.iter_content(chunk_size=chunk_size), pvalue_pb2.ParameterData
            ):
                yield ParameterData(message)

        return generate()

    def list_command_history(
        self,
        command: Optional[str] = None,
        queue: Optional[str] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        page_size: int = 500,
        descending: bool = False,
    ) -> Iterable[CommandHistory]:
        """
        Reads command history entries between the specified start and stop time.

        .. note::

            This method will send out multiple requests when more than
            ``page_size`` commands are queried. For large queries, consider
            using :meth:`stream_command_history` instead, it uses server-streaming
            based on a single request.

        :param command:
            Either a fully-qualified XTCE name or an alias in the
            format ``NAMESPACE/NAME``.
        :param queue:
            Name of the queue that the command was assigned to.
        :param start:
            Minimum generation time of the returned
            command history entries (inclusive)
        :param stop:
            Maximum generation time of the returned
            command history entries (exclusive)
        :param page_size:
            Page size of underlying requests. Higher values imply
            less overhead, but risk hitting the maximum message size
            limit.
        :param descending:
            If set to ``True`` results are fetched in reverse
            order (most recent first).
        """
        params: Dict[str, Any] = {
            "order": "desc" if descending else "asc",
        }
        if queue:
            params["queue"] = queue
        if page_size is not None:
            params["limit"] = page_size
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)

        if command:
            path = f"/archive/{self._instance}/commands{command}"
        else:
            path = f"/archive/{self._instance}/commands"

        return pagination.Iterator(
            ctx=self.ctx,
            path=path,
            params=params,
            response_class=commands_service_pb2.ListCommandsResponse,
            items_key="entry",
            item_mapper=CommandHistory,
        )

    def stream_command_history(
        self,
        name: Optional[Union[str, List[str]]] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        chunk_size: int = 32 * 1024,
    ) -> Iterable[CommandHistory]:
        """
        Reads command history between the specified start and stop time.

        .. versionadded:: 1.9.1

        :param name:
            If specified, return only commands with this name.
        :param start:
            Minimum generation time of the returned commands (inclusive)
        :param stop:
            Maximum generation time of the returned commands (exclusive)
        """
        options = commands_service_pb2.StreamCommandsRequest()
        if name is not None:
            if isinstance(name, str):
                options.name.extend([name])
            else:
                options.name.extend(name)
        if start is not None:
            options.start.MergeFrom(to_server_time(start))
        if stop is not None:
            options.stop.MergeFrom(to_server_time(stop))

        def generate():
            path = f"/stream-archive/{self._instance}:streamCommands"
            response = self.ctx.post_proto(
                path=path, data=options.SerializeToString(), stream=True
            )
            for message in split_protobuf_stream(
                response.iter_content(chunk_size=chunk_size),
                commanding_pb2.CommandHistoryEntry,
            ):
                yield CommandHistory(message)

        return generate()

    def list_tables(self) -> Iterable[Table]:
        """
        Returns the existing tables.

        Tables are returned in lexicographical order.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = f"/archive/{self._instance}/tables"
        response = self.ctx.get_proto(path=path)
        message = table_pb2.ListTablesResponse()
        message.ParseFromString(response.content)
        tables = getattr(message, "tables")
        return iter([Table(table) for table in tables])

    def get_table(self, table: str) -> Table:
        """
        Gets a single table.

        :param table:
            The name of the table.
        """
        path = f"/archive/{self._instance}/tables/{table}"
        response = self.ctx.get_proto(path=path)
        message = table_pb2.TableInfo()
        message.ParseFromString(response.content)
        return Table(message)

    def dump_table(
        self, table: str, query: Optional[str] = None, chunk_size: int = 32 * 1024
    ):
        path = f"/archive/{self._instance}/tables/{table}:readRows"
        if query:
            req = table_pb2.ReadRowsRequest()
            req.query = query
            response = self.ctx.post_proto(
                path=path, stream=True, data=req.SerializeToString()
            )
        else:
            response = self.ctx.post_proto(path=path, stream=True)
        return response.iter_content(chunk_size=chunk_size)

    def load_table(self, table: str, data, chunk_size: int = 32 * 1024) -> int:
        def read_in_chunks(file_object, chunk_size):
            chunk = file_object.read(chunk_size)
            while chunk:
                yield chunk
                chunk = file_object.read(chunk_size)

        path = f"/archive/{self._instance}/tables/{table}:writeRows"
        if chunk_size:
            generator = read_in_chunks(data, chunk_size)
            response = self.ctx.post_proto(path=path, data=generator)
        else:
            response = self.ctx.post_proto(path=path, data=data)
        message = table_pb2.WriteRowsResponse()
        message.ParseFromString(response.content)
        return message.count

    def rebuild_histogram(
        self,
        table: str,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
    ):
        """
        Rebuilds the histogram for a table. This may be necessary
        for example after bulk loading data.

        The rebuild may be constrained by using the
        ``start`` and ``stop`` parameters. When
        specified all partitions overlapping this range
        are reconsidered.

        .. note::
            Histogram rebuilds run synchronously: this
            method will await the outcome.

        :param table:
            The name of the table
        :param start:
            Start time
        :param stop:
            Stop time
        """
        req = table_pb2.RebuildHistogramRequest()
        if start:
            req.start.MergeFrom(to_server_time(start))
        if stop:
            req.stop.MergeFrom(to_server_time(stop))
        url = f"/archive/{self._instance}/tables/{table}:rebuildHistogram"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def rebuild_parameter_archive(
        self,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
    ):
        """
        Rebuilds the Parameter Archive.

        The rebuild may be constrained by using the
        ``start`` and ``stop`` parameters. These values
        are only hints to the Parameter Archive, which
        will extend the requested range based on archive
        segmentation.

        .. note::
            Rebuilds run as an asynchronous operation: this
            method will not await the outcome.

        :param start:
            Start time. This argument is optional since Yamcs v5.11.4
        :param stop:
            Stop time. This argument is optional since Yamcs v5.11.4
        """
        req = parameter_archive_service_pb2.RebuildRangeRequest()
        if start:
            req.start.MergeFrom(to_server_time(start))
        if stop:
            req.stop.MergeFrom(to_server_time(stop))
        url = f"/archive/{self._instance}/parameterArchive:rebuild"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def purge_parameter_archive(self):
        """
        Removes all Parameter Archive data and related metadata.

        Afterwards, use :meth:`rebuild_parameter_archive` to rebuild the Parameter
        Archive.
        """
        req = parameter_archive_service_pb2.PurgeRequest()
        url = f"/archive/{self._instance}/parameterArchive:purge"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def enable_parameter_archive_backfilling(self):
        """
        Enables the automatic backfilling (rebuilding) of the parameter archive.

        If the backfilling is already enabled, this operation has no effect.
        """
        req = parameter_archive_service_pb2.EnableBackfillingRequest()
        url = f"/archive/{self._instance}/parameterArchive:enableBackfilling"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def disable_parameter_archive_backfilling(self):
        """
        Disables the automatic backfilling (rebuilding) of the parameter archive.

        If the backfilling is already disabled, this operation has no effect.
        """
        req = parameter_archive_service_pb2.DisableBackfillingRequest()
        url = f"/archive/{self._instance}/parameterArchive:disableBackfilling"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def rebuild_ccsds_index(
        self,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
    ):
        """
        Rebuilds the CCSDS index. This is only applicable to projects that use a
        CcsdsTmIndex service to calculate packet completeness.

        .. note::
            Index rebuilds run synchronously: this
            method will await the outcome.

        :param start:
            Start time
        :param stop:
            Stop time
        """
        req = index_service_pb2.RebuildCcsdsIndexRequest()
        if start:
            req.start.MergeFrom(to_server_time(start))
        if stop:
            req.stop.MergeFrom(to_server_time(stop))
        url = f"/archive/{self._instance}:rebuildCcsdsIndex"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def list_streams(self) -> Iterable[Stream]:
        """
        Returns the existing streams.

        Streams are returned in lexicographical order.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = f"/archive/{self._instance}/streams"
        response = self.ctx.get_proto(path=path)
        message = table_pb2.ListStreamsResponse()
        message.ParseFromString(response.content)
        streams = getattr(message, "streams")
        return iter([Stream(stream) for stream in streams])

    def get_stream(self, stream: str) -> Stream:
        """
        Gets a single stream.

        :param stream:
            The name of the stream.
        """
        path = f"/archive/{self._instance}/streams/{stream}"
        response = self.ctx.get_proto(path=path)
        message = table_pb2.StreamInfo()
        message.ParseFromString(response.content)
        return Stream(message)

    def create_stream_subscription(
        self, stream: str, on_data: Callable[[StreamData], None], timeout: float = 60
    ) -> WebSocketSubscriptionFuture:
        """
        Create a new stream subscription.

        :param stream:
            The name of the stream.
        :param on_data:
            Function that gets called with  :class:`.StreamData`
            updates.
        :param timeout:
            The amount of seconds to wait for the request
            to complete.
        :return:
            Future that can be used to manage the background websocket
            subscription.
        """
        options = table_pb2.SubscribeStreamRequest()
        options.instance = self._instance
        options.stream = stream

        manager = WebSocketSubscriptionManager(
            self.ctx, topic="stream", options=options
        )

        # Represent subscription as a future
        subscription = WebSocketSubscriptionFuture(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_stream_data, subscription, on_data
        )

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def execute_sql(self, statement: str) -> ResultSet:
        """
        Executes a single SQL statement.

        :param statement:
            SQL string
        :return:
            A result set for consuming rows
        """
        path = f"/archive/{self._instance}:executeStreamingSql"
        req = table_pb2.ExecuteSqlRequest()
        req.statement = statement

        response = self.ctx.post_proto(
            path=path, data=req.SerializeToString(), stream=True
        )
        return ResultSet(response)
