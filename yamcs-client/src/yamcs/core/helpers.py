import logging
import os
from collections import OrderedDict
from datetime import datetime, timezone

from google.protobuf import timestamp_pb2
from google.protobuf.internal.decoder import _DecodeVarint32
from yamcs.core.exceptions import YamcsError
from yamcs.protobuf import yamcs_pb2

logger = logging.getLogger("yamcs-client")


def to_isostring(dt):
    """
    Converts the given datetime to an ISO String for use as URL parameter.
    """
    pb = to_server_time(dt)
    return pb.ToJsonString()


def to_server_time(dt):
    """
    Converts the given ``datetime.datetime`` to a
    ``google.protobuf.timestamp_pb2.Timestamp``.
    """
    if dt.tzinfo is None:
        # TODO - this is a temporary error.
        # Old versions of this client interpreted naive times as UTC,
        # but we would like to gradually adapt to use the system's
        # default instead. Until known users have adapted, the
        # safest solution is to just enforce a timezone.
        raise YamcsError(
            "Datetimes must be timezone-aware. For example: use "
            + "``datetime.now(tz=timezone.utc)`` instead of "
            + "``datetime.now()``"
        )

    pb = timestamp_pb2.Timestamp()
    pb.FromDatetime(dt)
    return pb


def parse_server_timestring(isostring):
    """
    Converts an ISO string to a timezone-aware ``datetime.datetime``.
    The timezone uses the system-default. This can be overriden to UTC
    by setting the environment variable ``PYTHON_YAMCS_CLIENT_UTC``.
    """
    if not isostring:
        return None
    naive = datetime.strptime(isostring.replace("Z", "GMT"), "%Y-%m-%dT%H:%M:%S.%f%Z")
    utctime = naive.replace(tzinfo=timezone.utc)

    if os.environ.get("PYTHON_YAMCS_CLIENT_UTC") not in (None, "0"):
        return utctime
    return utctime.astimezone(tz=None)


def parse_server_time(pb):
    """
    Converts a Protobuf timestamp message to a timezone-aware ``datetime.datetime``.
    The timezone uses the system-default. This can be overriden to UTC by setting
    the environment variable ``PYTHON_YAMCS_CLIENT_UTC``.
    """
    utctime = pb.ToDatetime().replace(tzinfo=timezone.utc)

    if os.environ.get("PYTHON_YAMCS_CLIENT_UTC") not in (None, "0"):
        return utctime
    return utctime.astimezone(tz=None)


def parse_value(proto):
    """
    Converts a Protobuf `Value` from the API into a python native value
    """
    if proto.type == yamcs_pb2.Value.FLOAT:
        return proto.floatValue
    elif proto.type == yamcs_pb2.Value.DOUBLE:
        return proto.doubleValue
    elif proto.type == yamcs_pb2.Value.SINT32:
        return proto.sint32Value
    elif proto.type == yamcs_pb2.Value.UINT32:
        return proto.uint32Value
    elif proto.type == yamcs_pb2.Value.BINARY:
        return proto.binaryValue
    elif proto.type == yamcs_pb2.Value.TIMESTAMP:
        # Don't use the actual 'timestampValue' field, it contains a number
        # that is difficult to interpret on the client. Instead parse from
        # the ISO String also set by Yamcs.
        return parse_server_timestring(proto.stringValue)
    elif proto.type == yamcs_pb2.Value.STRING:
        return proto.stringValue
    elif proto.type == yamcs_pb2.Value.UINT64:
        return proto.uint64Value
    elif proto.type == yamcs_pb2.Value.SINT64:
        return proto.sint64Value
    elif proto.type == yamcs_pb2.Value.BOOLEAN:
        return proto.booleanValue
    elif proto.type == yamcs_pb2.Value.ENUMERATED:
        return proto.stringValue
    elif proto.type == yamcs_pb2.Value.ARRAY:
        return [parse_value(v) for v in proto.arrayValue]
    elif proto.type == yamcs_pb2.Value.AGGREGATE:
        tuples = zip(proto.aggregateValue.name, proto.aggregateValue.value)
        return OrderedDict(map(lambda x: (x[0], parse_value(x[1])), tuples))
    elif proto.type == yamcs_pb2.Value.NONE:
        return None
    else:
        logger.warning("Unrecognized value type for update %s", proto)
        return None


def adapt_name_for_rest(name):
    """
    Modifies a user-provided name for use in API calls.
    Basically we want an alias like 'MDB:OPS Name/SIMULATOR_BatteryVoltage2'
    to be prepended with a slash.
    """
    if name.startswith("/"):
        return name
    elif "/" not in name:
        raise ValueError("Provided name is not a fully-qualified XTCE name.")
    return "/" + name


def to_named_object_id(parameter):
    """
    Builds a NamedObjectId. This is a bit more complex than it really
    should be. In Python (for convenience) we allow the user to simply address
    entries by their alias via the NAMESPACE/NAME convention. Yamcs is not
    aware of this convention so we decompose it into distinct namespace and
    name fields.
    """
    named_object_id = yamcs_pb2.NamedObjectId()
    if parameter.startswith("/"):
        named_object_id.name = parameter
    else:
        parts = parameter.split("/", 1)
        if len(parts) < 2:
            raise ValueError(
                f"Failed to process {parameter}. Use fully-qualified "
                "XTCE names or, alternatively, an alias in "
                "in the format NAMESPACE/NAME"
            )
        named_object_id.namespace = parts[0]
        named_object_id.name = parts[1]
    return named_object_id


def to_named_object_ids(parameters):
    """Builds a list of NamedObjectId."""
    if isinstance(parameters, str):
        return [to_named_object_id(parameters)]
    return [to_named_object_id(parameter) for parameter in parameters]


def split_protobuf_stream(chunk_iterator, message_class):
    buf = None
    for chunk in chunk_iterator:
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
            message = message_class()
            message.ParseFromString(msg_buf)
            yield message


class ProtoList(list):
    """
    List subclass to work with a list of wrapped items while
    maintaining the state in an underlying protobuf message.

    This assumes each wrapped item has an internal `_proto`
    field.
    """

    def __init__(self, parent_proto, items_key, item_mapper):
        self.parent_proto = parent_proto
        self.items_key = items_key
        self.item_mapper = item_mapper

    def __getitem__(self, index):
        repeatable = getattr(self.parent_proto, self.items_key)
        proto = repeatable.__getitem__(index)
        return self.item_mapper(proto)

    def __setitem__(self, index, value):
        repeatable = getattr(self.parent_proto, self.items_key)
        repeatable.__setitem__(index, value._proto)

    def __delitem__(self, __i):
        repeatable = getattr(self.parent_proto, self.items_key)
        return repeatable.__delitem__(__i)

    def __len__(self):
        repeatable = getattr(self.parent_proto, self.items_key)
        return repeatable.__len__()

    def __iter__(self):
        repeatable = getattr(self.parent_proto, self.items_key)
        return [self.item_mapper(proto) for proto in repeatable].__iter__()

    def __add__(self, __x):
        # Not obvious what should be the message_listener
        # of the returned repeated composite field container.
        raise TypeError(
            f"{self.__class__.__name__} object does not support list addition"
        )

    def __iadd__(self, __x):
        repeatable = getattr(self.parent_proto, self.items_key)
        protos = [item._proto for item in __x]
        repeatable.extend(protos)
        return self

    def reverse(self):
        repeatable = getattr(self.parent_proto, self.items_key)
        try:
            repeatable.reverse()
        except AttributeError:  # Only available since protobuf>=3.15
            raise TypeError(
                f"{self.__class__.__name__} object does not support reverse operation"
            ) from None

    def append(self, value):
        repeatable = getattr(self.parent_proto, self.items_key)
        repeatable.append(value._proto)

    def extend(self, __iterable):
        repeatable = getattr(self.parent_proto, self.items_key)
        repeatable.extend([value._proto for value in __iterable])

    def clear(self):
        repeatable = getattr(self.parent_proto, self.items_key)
        copy = list(repeatable)
        for item in copy:
            repeatable.remove(item)
