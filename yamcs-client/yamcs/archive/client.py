from yamcs.archive.model import IndexGroup, Packet
from yamcs.core import pagination
from yamcs.core.helpers import to_isostring
from yamcs.model import Event
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.archive import archive_pb2
from yamcs.protobuf.rest import rest_pb2
from yamcs.tmtc.model import ParameterValue


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


    def list_packet_histogram(self, name=None, start=None, stop=None, merge_time=2000):
        """
        Reads packet-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

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
            params['mergeTime'] = merge_time

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

    def list_processed_parameter_group_histogram(self, group=None, start=None, stop=None, merge_time=20000):
        """
        Reads index records related to processed parameter groups between the
        specified start and stop time.

        Each iteration returns a chunk of chronologically-sorted records.

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
            params['mergeTime'] = merge_time

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

    def list_event_histogram(self, source=None, start=None, stop=None, merge_time=2000):
        """
        Reads event-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

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
            params['mergeTime'] = merge_time

        return pagination.Iterator(
            client=self._client,
            path='/archive/{}/event-index'.format(self._instance),
            params=params,
            response_class=archive_pb2.IndexResponse,
            items_key='group',
            item_mapper=IndexGroup,
        )

    def list_command_histogram(self, name=None, start=None, stop=None, merge_time=2000):
        """
        Reads command-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

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
            params['mergeTime'] = merge_time

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

    def list_parameter_values(self, parameter, start=None, stop=None,
                              page_size=500, descending=False):
        """
        Reads parameter values between the specified start and stop time.

        :param ~datetime.datetime start: Minimum generation time of the returned
                                         values (inclusive)
        :param ~datetime.datetime stop: Maximum generation time of the returned
                                        values (exclusive)
        :param int page_size: Page size of underlying requests. Higher values imply
                              less overhead, but risk hitting the maximum message size limit.
        :param bool descending: If set to ``True`` values are fetched in reverse
                                order (most recent first).
        :rtype: ~collections.Iterable[.ParameterValue]
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

        return pagination.Iterator(
            client=self._client,
            path='/archive/{}/parameters{}'.format(self._instance, parameter),
            params=params,
            response_class=rest_pb2.ListParameterValuesResponse,
            items_key='parameter',
            item_mapper=ParameterValue,
        )
