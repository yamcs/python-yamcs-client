import functools
from datetime import datetime, timedelta, timezone

from yamcs.archive.model import (
    IndexGroup,
    ParameterRange,
    ResultSet,
    Sample,
    Stream,
    StreamData,
    Table,
)
from yamcs.core import pagination
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.helpers import to_isostring, to_server_time
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.model import Event
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.archive import (
    archive_pb2,
    index_service_pb2,
    parameter_archive_service_pb2,
)
from yamcs.protobuf.commanding import commands_service_pb2
from yamcs.protobuf.events import events_service_pb2
from yamcs.protobuf.packets import packets_service_pb2
from yamcs.protobuf.pvalue import pvalue_pb2
from yamcs.protobuf.table import table_pb2
from yamcs.tmtc.model import CommandHistory, Packet, ParameterValue


def _wrap_callback_parse_stream_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse StreamData
    from a WebSocket data message
    """
    pb = table_pb2.StreamData()
    message.Unpack(pb)
    on_data(StreamData(pb))


class ArchiveClient:
    def __init__(self, ctx, instance):
        super(ArchiveClient, self).__init__()
        self.ctx = ctx
        self._instance = instance

    def list_packet_names(self):
        """
        Returns the existing packet names.

        :rtype: ~collections.abc.Iterable[str]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = f"/archive/{self._instance}/packet-names"
        response = self.ctx.get_proto(path=path)
        message = packets_service_pb2.ListPacketNamesResponse()
        message.ParseFromString(response.content)
        names = getattr(message, "name")
        return iter(names)

    def list_packet_histogram(self, name=None, start=None, stop=None, merge_time=2):
        """
        Reads packet-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param float merge_time: Maximum gap in seconds before two consecutive index
                                 records are merged together.
        :rtype: ~collections.abc.Iterable[.IndexGroup]
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

    def list_processed_parameter_groups(self):
        """
        Returns the existing parameter groups.

        :rtype: ~collections.abc.Iterable[str]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = f"/archive/{self._instance}/parameter-groups"
        response = self.ctx.get_proto(path=path)
        message = archive_pb2.ParameterGroupInfo()
        message.ParseFromString(response.content)
        groups = getattr(message, "group")
        return iter(groups)

    def list_processed_parameter_group_histogram(
        self, group=None, start=None, stop=None, merge_time=20
    ):
        """
        Reads index records related to processed parameter groups between the
        specified start and stop time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param float merge_time: Maximum gap in seconds before two consecutive index
                                 records are merged together.
        :rtype: ~collections.abc.Iterable[.IndexGroup]
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

    def list_event_sources(self):
        """
        Returns the existing event sources.

        :rtype: ~collections.abc.Iterable[str]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = f"/archive/{self._instance}/events/sources"
        response = self.ctx.get_proto(path=path)
        message = events_service_pb2.ListEventSourcesResponse()
        message.ParseFromString(response.content)
        sources = getattr(message, "source")
        return iter(sources)

    def list_event_histogram(self, source=None, start=None, stop=None, merge_time=2):
        """
        Reads event-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param float merge_time: Maximum gap in seconds before two consecutive index
                                 records are merged together.
        :rtype: ~collections.abc.Iterable[.IndexGroup]
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

    def list_command_histogram(self, name=None, start=None, stop=None, merge_time=2):
        """
        Reads command-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param float merge_time: Maximum gap in seconds before two consecutive index
                                 records are merged together.
        :rtype: ~collections.abc.Iterable[.IndexGroup]
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

    def list_completeness_index(self, start=None, stop=None):
        """
        Reads completeness index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :rtype: ~collections.abc.Iterable[.IndexGroup]
        """
        params = {}
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/completeness-index",
            params=params,
            response_class=index_service_pb2.IndexResponse,
            items_key="group",
            item_mapper=IndexGroup,
        )

    def list_packets(
        self, name=None, start=None, stop=None, page_size=500, descending=False
    ):
        """
        Reads packet information between the specified start and stop
        time.

        Packets are sorted by generation time and sequence number.

        :param str name: Archived name of the packet
        :param ~datetime.datetime start: Minimum generation time of the returned
                                         packets (inclusive)
        :param ~datetime.datetime stop: Maximum generation time of the returned
                                        packets (exclusive)
        :param int page_size: Page size of underlying requests. Higher values imply
                              less overhead, but risk hitting the maximum message size
                              limit.
        :param bool descending: If set to ``True`` packets are fetched in reverse
                                order (most recent first).
        :rtype: ~collections.abc.Iterable[.Packet]
        """
        params = {
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

    def get_packet(self, generation_time, sequence_number):
        """
        Gets a single packet by its identifying key (gentime, seqNum).

        :param ~datetime.datetime generation_time: When the packet was generated
                                                   (packet time)
        :param int sequence_number: Sequence number of the packet
        :rtype: .Packet
        """
        url = f"/archive/{self._instance}/packets/"
        url += f"{to_isostring(generation_time)}/{sequence_number}"
        response = self.ctx.get_proto(url)
        message = yamcs_pb2.TmPacketData()
        message.ParseFromString(response.content)
        return Packet(message)

    def export_packets(self, name=None, start=None, stop=None, chunk_size=1024):
        """
        Export raw packets.

        Packets are sorted by generation time and sequence number.

        :param str name: Archived name of the packet
        :param ~datetime.datetime start: Minimum generation time of the returned
                                         packets (inclusive)
        :param ~datetime.datetime stop: Maximum generation time of the returned
                                        packets (exclusive)
        :rtype: An iterator over received chunks
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
        source=None,
        severity=None,
        text_filter=None,
        start=None,
        stop=None,
        page_size=500,
        descending=False,
    ):
        """
        Reads events between the specified start and stop time.

        Events are sorted by generation time, source, then sequence number.

        :param str source: The source of the returned events.
        :param str severity: The minimum severity level of the returned events.
                             One of ``INFO``, ``WATCH``, ``WARNING``, ``DISTRESS``,
                             ``CRITICAL`` or ``SEVERE``.
        :param str text_filter: Filter the text message of the returned events
        :param ~datetime.datetime start: Minimum start date of the returned events
                                         (inclusive)
        :param ~datetime.datetime stop: Maximum start date of the returned events
                                        (exclusive)
        :param int page_size: Page size of underlying requests. Higher values imply
                              less overhead, but risk hitting the maximum message size
                              limit.
        :param bool descending: If set to ``True`` events are fetched in reverse
                                order (most recent first).
        :rtype: ~collections.abc.Iterable[.Event]
        """
        params = {
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

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/events",
            params=params,
            response_class=events_service_pb2.ListEventsResponse,
            items_key="event",
            item_mapper=Event,
        )

    def sample_parameter_values(
        self,
        parameter,
        start=None,
        stop=None,
        sample_count=500,
        parameter_cache="realtime",
        source="ParameterArchive",
    ):
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

        :param str parameter: Either a fully-qualified XTCE name or an alias in the
                              format ``NAMESPACE/NAME``.
        :param ~datetime.datetime start: Minimum generation time of the sampled
                                         parameter values (inclusive). If not set
                                         this defaults to one hour ago.
        :param ~datetime.datetime stop: Maximum generation time of the sampled
                                        parameter values (exclusive). If not set
                                        this defaults to the current time.
        :param int sample_count: The number of returned samples.
        :param str parameter_cache: Specify the name of the processor who's
                                    parameter cache is merged with already
                                    archived values. To disable results from
                                    the parameter cache, set this to ``None``.
        :param str source: Specify how to retrieve parameter values. By
                           default this uses the ``ParameterArchive`` which
                           is optimized for retrieval. For Yamcs instances
                           that do not enable the ``ParameterArchive``, you can
                           still get results by specifying ``replay`` as the
                           source. Replay requests take longer to return because
                           the data needs to be reprocessed.
        :rtype: .Sample[]
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
        parameter,
        start=None,
        stop=None,
        min_gap=None,
        max_gap=None,
        parameter_cache="realtime",
    ):
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

        :param str parameter: Either a fully-qualified XTCE name or an alias in the
                              format ``NAMESPACE/NAME``.
        :param ~datetime.datetime start: Minimum generation time of the considered
                                         values (inclusive)
        :param ~datetime.datetime stop: Maximum generation time of the considered
                                        values (exclusive)
        :param float min_gap: Time in seconds. Any gap (detected based on parameter
                              expiration) smaller than this will be ignored.
                              However if the parameter changes value, the ranges
                              will still be split.
        :param float max_gap: Time in seconds. If the distance between two
                              subsequent parameter values is bigger than
                              this value (but smaller than the parameter
                              expiration), then an artificial gap is
                              created. This also applies if there is no
                              expiration defined for the parameter.
        :param str parameter_cache: Specify the name of the processor who's
                                    parameter cache is merged with already
                                    archived values. To disable results from
                                    the parameter cache, set this to ``None``.
        :rtype: .ParameterRange[]
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
        parameter,
        start=None,
        stop=None,
        page_size=500,
        descending=False,
        parameter_cache="realtime",
        source="ParameterArchive",
    ):
        """
        Reads parameter values between the specified start and stop time.

        :param str parameter: Either a fully-qualified XTCE name or an alias in the
                              format ``NAMESPACE/NAME``.
        :param ~datetime.datetime start: Minimum generation time of the returned
                                         values (inclusive)
        :param ~datetime.datetime stop: Maximum generation time of the returned
                                        values (exclusive)
        :param int page_size: Page size of underlying requests. Higher values imply
                              less overhead, but risk hitting the maximum message size
                              limit.
        :param bool descending: If set to ``True`` values are fetched in reverse
                                order (most recent first).
        :param str parameter_cache: Specify the name of the processor who's
                                    parameter cache is merged with already
                                    archived values. To disable results from
                                    the parameter cache, set this to ``None``.
        :param str source: Specify how to retrieve parameter values. By
                           default this uses the ``ParameterArchive`` which
                           is optimized for retrieval. For Yamcs instances
                           that do not enable the ``ParameterArchive``, you can
                           still get results by specifying ``replay`` as the
                           source. Replay requests take longer to return because
                           the data needs to be reprocessed.
        :rtype: ~collections.abc.Iterable[.ParameterValue]
        """
        params = {
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

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/archive/{self._instance}/parameters{parameter}",
            params=params,
            response_class=archive_pb2.ListParameterHistoryResponse,
            items_key="parameter",
            item_mapper=ParameterValue,
        )

    def list_command_history(
        self, command=None, start=None, stop=None, page_size=500, descending=False
    ):
        """
        Reads command history entries between the specified start and stop time.

        :param str command: Either a fully-qualified XTCE name or an alias in the
                            format ``NAMESPACE/NAME``.
        :param ~datetime.datetime start: Minimum generation time of the returned
                                         command history entries (inclusive)
        :param ~datetime.datetime stop: Maximum generation time of the returned
                                        command history entries (exclusive)
        :param int page_size: Page size of underlying requests. Higher values imply
                              less overhead, but risk hitting the maximum message size
                              limit.
        :param bool descending: If set to ``True`` results are fetched in reverse
                                order (most recent first).
        :rtype: ~collections.abc.Iterable[.CommandHistory]
        """
        params = {
            "order": "desc" if descending else "asc",
        }
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

    def list_tables(self):
        """
        Returns the existing tables.

        Tables are returned in lexicographical order.

        :rtype: ~collections.abc.Iterable[.Table]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = f"/archive/{self._instance}/tables"
        response = self.ctx.get_proto(path=path)
        message = table_pb2.ListTablesResponse()
        message.ParseFromString(response.content)
        tables = getattr(message, "tables")
        return iter([Table(table) for table in tables])

    def get_table(self, table):
        """
        Gets a single table.

        :param str table: The name of the table.
        :rtype: .Table
        """
        path = f"/archive/{self._instance}/tables/{table}"
        response = self.ctx.get_proto(path=path)
        message = table_pb2.TableInfo()
        message.ParseFromString(response.content)
        return Table(message)

    def dump_table(self, table, chunk_size=32 * 1024):
        path = f"/archive/{self._instance}/tables/{table}:readRows"
        response = self.ctx.post_proto(path=path, stream=True)
        return response.iter_content(chunk_size=chunk_size)

    def load_table(self, table, data, chunk_size=32 * 1024):
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

    def rebuild_histogram(self, table, start=None, stop=None):
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

        :param str table: The name of the table
        :param start: Start time
        :type start: Optional[~datetime.datetime]
        :param stop: Stop time
        :type stop: Optional[~datetime.datetime]
        """
        req = table_pb2.RebuildHistogramRequest()
        if start:
            req.start.MergeFrom(to_server_time(start))
        if stop:
            req.stop.MergeFrom(to_server_time(stop))
        url = f"/archive/{self._instance}/tables/{table}:rebuildHistogram"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def rebuild_parameter_archive(self, start, stop):
        """
        Rebuilds the Parameter Archive.

        The rebuild must be constrained by using the
        ``start`` and ``stop`` parameters. This values
        are only hints to the Parameter Archive, which
        will extend the requested range based on archive
        segmentation.

        .. note::
            Rebuilds run as an asynchronous operation: this
            method will not await the outcome.

        :param start: Start time
        :type start: ~datetime.datetime
        :param stop: Stop time
        :type stop: ~datetime.datetime
        """
        req = parameter_archive_service_pb2.RebuildRangeRequest()
        req.start.MergeFrom(to_server_time(start))
        req.stop.MergeFrom(to_server_time(stop))
        url = f"/archive/{self._instance}/parameterArchive:rebuild"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def list_streams(self):
        """
        Returns the existing streams.

        Streams are returned in lexicographical order.

        :rtype: ~collections.abc.Iterable[.Stream]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = f"/archive/{self._instance}/streams"
        response = self.ctx.get_proto(path=path)
        message = table_pb2.ListStreamsResponse()
        message.ParseFromString(response.content)
        streams = getattr(message, "streams")
        return iter([Stream(stream) for stream in streams])

    def get_stream(self, stream):
        """
        Gets a single stream.

        :param str stream: The name of the stream.
        :rtype: .Stream
        """
        path = f"/archive/{self._instance}/streams/{stream}"
        response = self.ctx.get_proto(path=path)
        message = table_pb2.StreamInfo()
        message.ParseFromString(response.content)
        return Stream(message)

    def create_stream_subscription(self, stream, on_data, timeout=60):
        """
        Create a new stream subscription.

        :param str stream: The name of the stream.
        :param on_data: Function that gets called with  :class:`.StreamData`
                        updates.
        :param float timeout: The amount of seconds to wait for the request
                              to complete.
        :return: Future that can be used to manage the background websocket
                 subscription
        :rtype: .WebSocketSubscriptionFuture
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

    def execute_sql(self, statement):
        """
        Executes a single SQL statement.

        :param statement: SQL string
        :return: A result set for consuming rows
        :rtype: .ResultSet
        """
        path = f"/archive/{self._instance}:executeStreamingSql"
        req = table_pb2.ExecuteSqlRequest()
        req.statement = statement

        response = self.ctx.post_proto(
            path=path, data=req.SerializeToString(), stream=True
        )
        return ResultSet(response)
