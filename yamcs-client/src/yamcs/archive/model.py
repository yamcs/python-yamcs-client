from google.protobuf.internal.decoder import _DecodeVarint32
from yamcs.core.helpers import parse_server_timestring, parse_value
from yamcs.protobuf.table import table_pb2


class Table:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Table name."""
        return self._proto.name

    def __str__(self):
        return self.name


class Stream:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Stream name."""
        return self._proto.name

    def __str__(self):
        return self.name


class StreamData:
    def __init__(self, proto):
        self._proto = proto

    @property
    def stream(self):
        """Stream name."""
        return self._proto.stream

    @property
    def columns(self):
        """Tuple columns."""
        return [ColumnData(c) for c in self._proto.column]

    def __str__(self):
        return f"{self.stream} ({len(self.columns)} columns)"


class ColumnData:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Column name."""
        return self._proto.name

    @property
    def value(self):
        """Value for this column."""
        return parse_value(self._proto.value)

    def __str__(self):
        return f"{self.name}: {self.value}"


class ResultSet:
    """
    Provides capability to consume the rows returned by a
    SQL query, or access related information.
    """

    def __init__(self, response):
        self._response = response
        self._columns_proto = None  # Set after first read

    def __iter__(self):
        buf = None
        for chunk in self._response.iter_content(chunk_size=4096):
            if buf is None:
                buf = chunk
            else:
                buf += chunk

            while len(buf):
                try:
                    # n is advanced beyond the varint
                    msg_len, n = _DecodeVarint32(buf, 0)
                except IndexError:
                    break  # Need another chunk

                if n + msg_len > len(buf):
                    break  # Need another chunk

                msg_buf = buf[n : (n + msg_len)]
                buf = buf[(n + msg_len) :]
                message = table_pb2.ResultSet()
                message.ParseFromString(msg_buf)
                if self._columns_proto is None:
                    self._columns_proto = message.columns
                for row_proto in message.rows:
                    values = [parse_value(v) for v in row_proto.values]
                    yield values

    @property
    def columns(self):
        """
        Column names. This returns ``None`` as long as no row has
        been consumed yet.

        :type: str[]
        """
        if self._columns_proto is not None:
            return [c.name for c in self._columns_proto]
        return None

    @property
    def column_types(self):
        """
        Column types.

        :type: str[]
        """
        if self._columns_proto is not None:
            return [c.type for c in self._columns_proto]
        return None


class IndexGroup:
    """
    Group of index records that represent the same
    type of underlying objects.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """
        Name associated with this group. The meaning is defined
        by the objects represented by this index. For example:

        * In an index of events, index records are grouped by ``source``.
        * In an index of packets, index records are grouped by ``packet name``.
        """
        if self._proto.HasField("id"):
            return self._proto.id.name
        return None

    @property
    def records(self):
        """
        Index records within this group

        :type: List[:class:`.IndexRecord`]
        """
        return [IndexRecord(rec) for rec in self._proto.entry]

    def __str__(self):
        return f"{self.name} ({len(self.records)} records)"


class IndexRecord:
    """
    Represents a block of uninterrupted data (derived from the index definition
    for the type of underlying objects, in combination with the requested
    ``merge_time``.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def start(self):
        """
        Start time of the record

        :type: :class:`~datetime.datetime`
        """
        return parse_server_timestring(self._proto.start)

    @property
    def stop(self):
        """
        Stop time of the record

        :type: :class:`~datetime.datetime`
        """
        return parse_server_timestring(self._proto.stop)

    @property
    def count(self):
        """
        Number of underlying objects this index record represents
        """
        return self._proto.count

    def __str__(self):
        return f"{self.start} - {self.stop} (n={self.count})"


class Sample:
    """
    Provides aggregation properties over a range of a parameter's
    values.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def time(self):
        """
        Sample time.

        :type: :class:`~datetime.datetime`
        """
        return parse_server_timestring(self._proto.time)

    @property
    def avg(self):
        """Average value."""
        if self._proto.HasField("avg"):
            return self._proto.avg
        return None

    @property
    def min(self):
        """Minimum value."""
        if self._proto.HasField("min"):
            return self._proto.min
        return None

    @property
    def max(self):
        """Maximum value."""
        if self._proto.HasField("max"):
            return self._proto.max
        return None

    @property
    def parameter_count(self):
        """The number of parameter values this sample represents."""
        return self._proto.n

    def __str__(self):
        return f"{self.time} {self.avg}"


class ParameterRange:
    """
    Indicates an interval during which a parameter's
    value was uninterrupted and unchanged.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def start(self):
        """
        Start time of this range (inclusive).

        :type: :class:`~datetime.datetime`
        """
        return parse_server_timestring(self._proto.timeStart)

    @property
    def stop(self):
        """
        Stop time of this range (exclusive).

        :type: :class:`~datetime.datetime`
        """
        return parse_server_timestring(self._proto.timeStop)

    @property
    def eng_value(self):
        """The engineering (calibrated) value."""
        return parse_value(self._proto.engValue)

    @property
    def parameter_count(self):
        """The number of received parameter values during this range."""
        return self._proto.count

    def __str__(self):
        return f"{self.start} - {self.stop}: {self.eng_value}"
