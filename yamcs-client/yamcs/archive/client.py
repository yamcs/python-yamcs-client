from yamcs.archive.model import IndexChunk, Packet
from yamcs.core import pagination
from yamcs.core.helpers import to_isostring
from yamcs.model import Event
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.archive import archive_pb2
from yamcs.protobuf.rest import rest_pb2


class ArchiveClient(object):

    def __init__(self, client, instance):
        super(ArchiveClient, self).__init__()
        self._client = client
        self._instance = instance

    def list_packet_names(self):
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

        :rtype: :class:`.IndexChunk` iterator
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
            item_mapper=IndexChunk,
        )

    def list_processed_parameter_groups(self):
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

        :rtype: :class:`.IndexChunk` iterator
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
            item_mapper=IndexChunk,
        )

    def list_event_sources(self):
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

        :rtype: :class:`.IndexChunk` iterator
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
            item_mapper=IndexChunk,
        )

    def list_command_histogram(self, name=None, start=None, stop=None, merge_time=2000):
        """
        Reads command-related index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :rtype: :class:`.IndexChunk` iterator
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
            item_mapper=IndexChunk,
        )

    def list_completeness_index(self, start=None, stop=None):
        """
        Reads completeness index records between the specified start and stop
        time.

        Each iteration returns a chunk of chronologically-sorted records.

        :rtype: :class:`.IndexChunk` iterator
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
            item_mapper=IndexChunk,
        )

    def list_packets(self, name=None, start=None, stop=None, page_size=500, descending=False):
        """
        Reads packet information between the specified start and stop
        time.

        Packets are sorted by generation time and sequence number.

        :rtype: :class:`.Packet` iterator
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

    def get_packet(self, generation_time, sequenceNumber):
        """
        Gets a single packet by its identifying key (gentime, seqNum).

        :param generation_time: datetime.
        :rtype: :class:`.Packet`
        """
        url = '/archive/{}/packets/{}/{}'.format(
            self._instance, to_isostring(generation_time), sequenceNumber)
        response = self._client.get_proto(url)
        message = yamcs_pb2.TmPacketData()
        message.ParseFromString(response.content)
        return Packet(message)

    def list_events(self, source=None, severity=None, text_filter=None,
                    start=None, stop=None, page_size=500, descending=False):
        """
        Reads events between the specified start and stop time.

        Events are sorted by generation time and sequence number.

        :rtype: :class:`.Event` iterator
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
