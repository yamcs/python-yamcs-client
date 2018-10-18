import functools
from datetime import datetime, timedelta

from yamcs.archive.model import (IndexGroup, Packet, ParameterRange, Sample,
                                 Stream, StreamData, Table)
from yamcs.core import pagination
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.helpers import to_isostring
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.model import Event
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.archive import archive_pb2
from yamcs.protobuf.pvalue import pvalue_pb2
from yamcs.protobuf.rest import rest_pb2
from yamcs.protobuf.table import table_pb2
from yamcs.tmtc.model import CommandHistory, ParameterValue


def _wrap_callback_parse_stream_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse StreamData
    from a WebSocket data message
    """
    if (message.type == message.DATA and
            message.data.type == yamcs_pb2.STREAM_DATA):
        stream_data = getattr(message.data, 'streamData')
        on_data(StreamData(stream_data))


class ArchiveClient(object):

    def __init__(self, client, instance):
        super(ArchiveClient, self).__init__()
        self._client = client
        self._instance = instance

    def list_packet_names(self):
        """
        Returns the existing packet names.

        :rtype: ~collections.Iterable[str]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = '/archive/{}/packet-names'.format(self._instance)
        response = self._client.get_proto(path=path)
        message = archive_pb2.GetPacketNamesResponse()
        message.ParseFromString(response.content)
        names = getattr(message, 'name')
        return iter(names)

    def list_packet_histogram(self, name=None, start=None, stop=None, merge_time=2):
        """
        Reads packet-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param float merge_time: Maximum gap in seconds before two consecutive index records are merged together.
        :rtype: ~collections.Iterable[.IndexGroup]
        """
        params = {}
        if name is not None:
            params['name'] = name
        if start is not None:
            params['start'] = to_isostring(start)
        if stop is not None:
            params['stop'] = to_isostring(stop)
        if merge_time is not None:
            params['mergeTime'] = int(merge_time * 1000)

        return pagination.Iterator(
            client=self._client,
            path='/archive/{}/packet-index'.format(self._instance),
            params=params,
            response_class=archive_pb2.IndexResponse,
            items_key='group',
            item_mapper=IndexGroup,
        )

    def list_processed_parameter_groups(self):
        """
        Returns the existing parameter groups.

        :rtype: ~collections.Iterable[str]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = '/archive/{}/parameter-groups'.format(self._instance)
        response = self._client.get_proto(path=path)
        message = archive_pb2.ParameterGroupInfo()
        message.ParseFromString(response.content)
        groups = getattr(message, 'group')
        return iter(groups)

    def list_processed_parameter_group_histogram(self, group=None, start=None, stop=None, merge_time=20):
        """
        Reads index records related to processed parameter groups between the
        specified start and stop time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param float merge_time: Maximum gap in seconds before two consecutive index records are merged together.
        :rtype: ~collections.Iterable[.IndexGroup]
        """
        params = {}
        if group is not None:
            params['group'] = group
        if start is not None:
            params['start'] = to_isostring(start)
        if stop is not None:
            params['stop'] = to_isostring(stop)
        if merge_time is not None:
            params['mergeTime'] = int(merge_time * 1000)

        return pagination.Iterator(
            client=self._client,
            path='/archive/{}/parameter-index'.format(self._instance),
            params=params,
            response_class=archive_pb2.IndexResponse,
            items_key='group',
            item_mapper=IndexGroup,
        )

    def list_event_sources(self):
        """
        Returns the existing event sources.

        :rtype: ~collections.Iterable[str]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = '/archive/{}/events/sources'.format(self._instance)
        response = self._client.get_proto(path=path)
        message = archive_pb2.EventSourceInfo()
        message.ParseFromString(response.content)
        sources = getattr(message, 'source')
        return iter(sources)

    def list_event_histogram(self, source=None, start=None, stop=None, merge_time=2):
        """
        Reads event-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param float merge_time: Maximum gap in seconds before two consecutive index records are merged together.
        :rtype: ~collections.Iterable[.IndexGroup]
        """
        params = {}
        if source is not None:
            params['source'] = source
        if start is not None:
            params['start'] = to_isostring(start)
        if stop is not None:
            params['stop'] = to_isostring(stop)
        if merge_time is not None:
            params['mergeTime'] = int(merge_time * 1000)

        return pagination.Iterator(
            client=self._client,
            path='/archive/{}/event-index'.format(self._instance),
            params=params,
            response_class=archive_pb2.IndexResponse,
            items_key='group',
            item_mapper=IndexGroup,
        )

    def list_command_histogram(self, name=None, start=None, stop=None, merge_time=2):
        """
        Reads command-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :param float merge_time: Maximum gap in seconds before two consecutive index records are merged together.
        :rtype: ~collections.Iterable[.IndexGroup]
        """
        params = {}
        if name is not None:
            params['name'] = name
        if start is not None:
            params['start'] = to_isostring(start)
        if stop is not None:
            params['stop'] = to_isostring(stop)
        if merge_time is not None:
            params['mergeTime'] = int(merge_time * 1000)

        return pagination.Iterator(
            client=self._client,
            path='/archive/{}/command-index'.format(self._instance),
            params=params,
            response_class=archive_pb2.IndexResponse,
            items_key='group',
            item_mapper=IndexGroup,
        )

    def list_completeness_index(self, start=None, stop=None):
        """
        Reads completeness index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :rtype: ~collections.Iterable[.IndexGroup]
        """
        params = {}
        if start is not None:
            params['start'] = to_isostring(start)
        if stop is not None:
            params['stop'] = to_isostring(stop)

        return pagination.Iterator(
            client=self._client,
            path='/archive/{}/completeness-index'.format(self._instance),
            params=params,
            response_class=archive_pb2.IndexResponse,
            items_key='group',
            item_mapper=IndexGroup,
        )

    def list_packets(self, name=None, start=None, stop=None, page_size=500, descending=False):
        """
        Reads packet information between the specified start and stop
        time.

        Packets are sorted by generation time and sequence number.

        :param ~datetime.datetime start: Minimum generation time of the returned
                                         packets (inclusive)
        :param ~datetime.datetime stop: Maximum genreation time of the returned
                                        packets (exclusive)
        :param int page_size: Page size of underlying requests. Higher values imply
                              less overhead, but risk hitting the maximum message size limit.
        :param bool descending: If set to ``True`` packets are fetched in reverse
                                order (most recent first).
        :rtype: ~collections.Iterable[.Packet]
        """
        params = {
            'order': 'desc' if descending else 'asc',
        }
        if name is not None:
            params['name'] = name
        if page_size is not None:
            params['limit'] = page_size
        if start is not None:
            params['start'] = to_isostring(start)
        if stop is not None:
            params['stop'] = to_isostring(stop)

        return pagination.Iterator(
            client=self._client,
            path='/archive/{}/packets'.format(self._instance),
            params=params,
            response_class=rest_pb2.ListPacketsResponse,
            items_key='packet',
            item_mapper=Packet,
        )

    def get_packet(self, generation_time, sequence_number):
        """
        Gets a single packet by its identifying key (gentime, seqNum).

        :param ~datetime.datetime generation_time: When the packet was generated (packet time)
        :param int sequence_number: Sequence number of the packet
        :rtype: .Packet
        """
        url = '/archive/{}/packets/{}/{}'.format(
            self._instance, to_isostring(generation_time), sequence_number)
        response = self._client.get_proto(url)
        message = yamcs_pb2.TmPacketData()
        message.ParseFromString(response.content)
        return Packet(message)

    def list_events(self, source=None, severity=None, text_filter=None,
                    start=None, stop=None, page_size=500, descending=False):
        """
        Reads events between the specified start and stop time.

        Events are sorted by generation time, source, then sequence number.

        :param str source: The source of the returned events.
        :param str severity: The minimum severity level of the returned events.
                             One of ``INFO``, ``WATCH``, ``WARNING``, ``DISTRESS``,
                             ``CRITICAL`` or ``SEVERE``.
        :param str text_filter: Filter the text message of the returned events
        :param ~datetime.datetime start: Minimum start date of the returned events (inclusive)
        :param ~datetime.datetime stop: Maximum start date of the returned events (exclusive)
        :param int page_size: Page size of underlying requests. Higher values imply
                              less overhead, but risk hitting the maximum message size limit.
        :param bool descending: If set to ``True`` events are fetched in reverse
                                order (most recent first).
        :rtype: ~collections.Iterable[.Event]
        """
        params = {
            'order': 'desc' if descending else 'asc',
        }
        if source is not None:
            params['source'] = source
        if page_size is not None:
            params['limit'] = page_size
        if severity is not None:
            params['severity'] = severity
        if start is not None:
            params['start'] = to_isostring(start)
        if stop is not None:
            params['stop'] = to_isostring(stop)
        if text_filter is not None:
            params['q'] = text_filter

        return pagination.Iterator(
            client=self._client,
            path='/archive/{}/events'.format(self._instance),
            params=params,
            response_class=rest_pb2.ListEventsResponse,
            items_key='event',
            item_mapper=Event,
        )

    def sample_parameter_values(self, parameter, start=None, stop=None,
                                sample_count=500, parameter_cache='realtime',
                                source='ParameterArchive'):
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
        path = '/archive/{}/parameters{}/samples'.format(
            self._instance, parameter)
        now = datetime.utcnow()
        params = {
            'count': sample_count,
            'source': source,
            'start': to_isostring(now - timedelta(hours=1)),
            'stop': to_isostring(now),
        }
        if start is not None:
            params['start'] = to_isostring(start)
        if stop is not None:
            params['stop'] = to_isostring(stop)

        if parameter_cache:
            params['processor'] = parameter_cache
        else:
            params['norealtime'] = True

        response = self._client.get_proto(path=path, params=params)
        message = pvalue_pb2.TimeSeries()
        message.ParseFromString(response.content)
        samples = getattr(message, 'sample')
        return [Sample(s) for s in samples]

    def list_parameter_ranges(self, parameter, start=None, stop=None,
                              min_gap=None, max_gap=None,
                              parameter_cache='realtime'):
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
        path = '/archive/{}/parameters{}/ranges'.format(
            self._instance, parameter)
        params = {}
        if start is not None:
            params['start'] = to_isostring(start)
        if stop is not None:
            params['stop'] = to_isostring(stop)
        if min_gap is not None:
            params['minGap'] = int(min_gap * 1000)
        if max_gap is not None:
            params['maxGap'] = int(max_gap * 1000)

        if parameter_cache:
            params['processor'] = parameter_cache
        else:
            params['norealtime'] = True

        response = self._client.get_proto(path=path, params=params)
        message = pvalue_pb2.Ranges()
        message.ParseFromString(response.content)
        ranges = getattr(message, 'range')
        return [ParameterRange(r) for r in ranges]

    def list_parameter_values(self, parameter, start=None, stop=None,
                              page_size=500, descending=False,
                              parameter_cache='realtime',
                              source='ParameterArchive'):
        """
        Reads parameter values between the specified start and stop time.

        :param str parameter: Either a fully-qualified XTCE name or an alias in the
                              format ``NAMESPACE/NAME``.
        :param ~datetime.datetime start: Minimum generation time of the returned
                                         values (inclusive)
        :param ~datetime.datetime stop: Maximum generation time of the returned
                                        values (exclusive)
        :param int page_size: Page size of underlying requests. Higher values imply
                              less overhead, but risk hitting the maximum message size limit.
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
        :rtype: ~collections.Iterable[.ParameterValue]
        """
        params = {
            'source': source,
            'order': 'desc' if descending else 'asc',
        }
        if page_size is not None:
            params['limit'] = page_size
        if start is not None:
            params['start'] = to_isostring(start)
        if stop is not None:
            params['stop'] = to_isostring(stop)

        if parameter_cache:
            params['processor'] = parameter_cache
        else:
            params['norealtime'] = True

        return pagination.Iterator(
            client=self._client,
            path='/archive/{}/parameters{}'.format(self._instance, parameter),
            params=params,
            response_class=rest_pb2.ListParameterValuesResponse,
            items_key='parameter',
            item_mapper=ParameterValue,
        )

    def list_command_history(self, command=None, start=None, stop=None,
                             page_size=500, descending=False):
        """
        Reads command history entries between the specified start and stop time.

        :param str command: Either a fully-qualified XTCE name or an alias in the
                            format ``NAMESPACE/NAME``.
        :param ~datetime.datetime start: Minimum generation time of the returned
                                         command history entries (inclusive)
        :param ~datetime.datetime stop: Maximum generation time of the returned
                                        command history entries (exclusive)
        :param int page_size: Page size of underlying requests. Higher values imply
                              less overhead, but risk hitting the maximum message size limit.
        :param bool descending: If set to ``True`` results are fetched in reverse
                                order (most recent first).
        :rtype: ~collections.Iterable[.CommandHistory]
        """
        params = {
            'order': 'desc' if descending else 'asc',
        }
        if page_size is not None:
            params['limit'] = page_size
        if start is not None:
            params['start'] = to_isostring(start)
        if stop is not None:
            params['stop'] = to_isostring(stop)

        if command:
            path = '/archive/{}/commands{}'.format(self._instance, command)
        else:
            path = '/archive/{}/commands'.format(self._instance)

        return pagination.Iterator(
            client=self._client,
            path=path,
            params=params,
            response_class=rest_pb2.ListCommandsResponse,
            items_key='entry',
            item_mapper=CommandHistory,
        )

    def list_tables(self):
        """
        Returns the existing tables.

        Tables are returned in lexicographical order.

        :rtype: ~collections.Iterable[.Table]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = '/archive/{}/tables'.format(self._instance)
        response = self._client.get_proto(path=path)
        message = rest_pb2.ListTablesResponse()
        message.ParseFromString(response.content)
        tables = getattr(message, 'table')
        return iter([Table(table) for table in tables])

    def get_table(self, table):
        """
        Gets a single table.

        :param str table: The name of the table.
        :rtype: .Table
        """
        path = '/archive/{}/tables/{}'.format(self._instance, table)
        response = self._client.get_proto(path=path)
        message = archive_pb2.TableInfo()
        message.ParseFromString(response.content)
        return Table(message)

    def dump_table(self, table, chunk_size=1024):
        path = '/archive/{}/downloads/tables/{}'.format(self._instance, table)
        params = {'format': 'dump'}
        response = self._client.get_proto(path=path, stream=True, params=params)
        return response.iter_content(chunk_size=chunk_size)

    def load_table(self, table, data):
        path = '/archive/{}/tables/{}/data'.format(self._instance, table)
        response = self._client.post_proto(path=path, data=data)
        message = table_pb2.TableLoadResponse()
        message.ParseFromString(response.content)
        return message.rowsLoaded

    def list_streams(self):
        """
        Returns the existing streams.

        Streams are returned in lexicographical order.

        :rtype: ~collections.Iterable[.Stream]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        path = '/archive/{}/streams'.format(self._instance)
        response = self._client.get_proto(path=path)
        message = rest_pb2.ListStreamsResponse()
        message.ParseFromString(response.content)
        streams = getattr(message, 'stream')
        return iter([Stream(stream) for stream in streams])

    def get_stream(self, stream):
        """
        Gets a single stream.

        :param str stream: The name of the stream.
        :rtype: .Stream
        """
        path = '/archive/{}/streams/{}'.format(self._instance, stream)
        response = self._client.get_proto(path=path)
        message = archive_pb2.StreamInfo()
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
        options = rest_pb2.StreamSubscribeRequest()
        options.stream = stream

        manager = WebSocketSubscriptionManager(
            self._client, resource='stream', options=options)

        # Represent subscription as a future
        subscription = WebSocketSubscriptionFuture(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_stream_data, subscription, on_data)

        manager.open(wrapped_callback, instance=self._instance)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def execute_sql(self, statement):
        """
        Executes a single SQL statement.

        :param statement: SQL string
        :return: String response
        :rtype: str
        """
        path = '/archive/{}/sql'.format(self._instance)
        req = archive_pb2.ExecuteSqlRequest()
        req.statement = statement

        response = self._client.post_proto(path=path,
                                           data=req.SerializeToString())
        message = archive_pb2.ExecuteSqlResponse()
        message.ParseFromString(response.content)
        if message.HasField('result'):
            return message.result
        return None
