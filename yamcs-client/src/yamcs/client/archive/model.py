import datetime
from typing import Any, List, Optional

from google.protobuf.internal.decoder import _DecodeVarint32
from yamcs.client.core.helpers import (
    parse_server_time,
    parse_server_timestring,
    parse_value,
)
from yamcs.protobuf.table import table_pb2

__all__ = [
    "ColumnData",
    "IndexGroup",
    "IndexRecord",
    "ParameterRange",
    "ParameterRangeEntry",
    "ResultSet",
    "Sample",
    "Stream",
    "StreamData",
    "Table",
]


class Table:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Table name."""
        return self._proto.name

    def __str__(self):
        return self.name


class Stream:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Stream name."""
        return self._proto.name

    def __str__(self):
        return self.name


class StreamData:
    def __init__(self, proto):
        self._proto = proto

    @property
    def stream(self) -> str:
        """Stream name."""
        return self._proto.stream

    @property
    def columns(self) -> List["ColumnData"]:
        """Tuple columns."""
        return [ColumnData(c) for c in self._proto.column]

    def __str__(self):
        return f"{self.stream} ({len(self.columns)} columns)"


class ColumnData:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Column name."""
        return self._proto.name

    @property
    def value(self) -> Any:
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
    def columns(self) -> Optional[List[str]]:
        """
        Column names. This returns ``None`` as long as no row has
        been consumed yet.
        """
        if self._columns_proto is not None:
            return [c.name for c in self._columns_proto]
        return None

    @property
    def column_types(self) -> Optional[List[str]]:
        """
        Column types.
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
    def name(self) -> str:
        """
        Name associated with this group. The meaning is defined
        by the objects represented by this index. For example:

        * In an index of events, index records are grouped by ``source``.
        * In an index of packets, index records are grouped by ``packet name``.
        """
        return self._proto.id.name

    @property
    def records(self) -> List["IndexRecord"]:
        """
        Index records within this group
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
    def start(self) -> datetime.datetime:
        """
        Start time of the record
        """
        return parse_server_timestring(self._proto.start)

    @property
    def stop(self) -> datetime.datetime:
        """
        Stop time of the record
        """
        return parse_server_timestring(self._proto.stop)

    @property
    def count(self) -> int:
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
    def time(self) -> datetime.datetime:
        """
        Sample time.
        """
        return parse_server_time(self._proto.time)

    @property
    def avg(self) -> Optional[float]:
        """Average value."""
        if self._proto.HasField("avg"):
            return self._proto.avg
        return None

    @property
    def min(self) -> Optional[float]:
        """Minimum value."""
        if self._proto.HasField("min"):
            return self._proto.min
        return None

    @property
    def max(self) -> Optional[float]:
        """Maximum value."""
        if self._proto.HasField("max"):
            return self._proto.max
        return None

    @property
    def parameter_count(self) -> int:
        """The number of parameter values this sample represents."""
        return self._proto.n

    def __str__(self):
        return f"{self.time} {self.avg}"


class ParameterRangeEntry:
    """
    Value holder for an engineering value and its
    number of appearances within a ParameterRange.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def eng_value(self) -> Any:
        """The engineering (calibrated) value."""
        return parse_value(self._proto.engValue)

    @property
    def parameter_count(self) -> int:
        """The number of received parameter values during this range."""
        return self._proto.count

    def __str__(self):
        return f"{self.eng_value} {self.parameter_count}x"


class ParameterRange:
    """
    Indicates an interval during which a parameter's
    value was uninterrupted and unchanged.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def start(self) -> datetime.datetime:
        """
        Start time of this range (inclusive).
        """
        return parse_server_time(self._proto.start)

    @property
    def stop(self) -> datetime.datetime:
        """
        Stop time of this range (exclusive).
        """
        return parse_server_time(self._proto.stop)

    @property
    def eng_value(self) -> Optional[Any]:
        """
        The engineering (calibrated) value within this range.

        If the request was made using ``min_range`` option,
        this will be the most-frequent value only. Retrieve
        the complete distribution using the ``entries``
        attribute.
        """
        max_count = None
        result = None
        for idx, count in enumerate(self._proto.counts):
            if max_count is None or (count > max_count):
                max_count = count
                result = self._proto.engValues[idx]

        if result:
            return parse_value(result)
        else:
            return None

    @property
    def parameter_count(self) -> int:
        """
        The total number of parameter values within this range.
        """
        return self._proto.count

    @property
    def entries(self) -> List[ParameterRangeEntry]:
        """
        Value distribution within this range.

        Unless the request was made using ``min_range`` option,
        there should be only one entry only.
        """
        return [ParameterRangeEntry(proto) for proto in self._proto.engValues]

    def __str__(self):
        return f"{self.start} - {self.stop}: {self.eng_value}"
