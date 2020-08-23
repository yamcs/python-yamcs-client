import logging
from collections import OrderedDict
from datetime import datetime, timezone

from google.protobuf import timestamp_pb2

from yamcs.protobuf import yamcs_pb2


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
        logging.warning(
            "A datetime without tzinfo is naively interpreted as UTC. "
            + "Make your datetime timezone-aware to avoid this message"
        )

    pb = timestamp_pb2.Timestamp()
    pb.FromDatetime(dt)
    return pb


def parse_server_timestring(isostring):
    """
    Parse the ISO String to a UTC ``datetime.datetime``.
    """
    if not isostring:
        return None
    naive = datetime.strptime(isostring.replace("Z", "GMT"), "%Y-%m-%dT%H:%M:%S.%f%Z")
    return naive.replace(tzinfo=timezone.utc)


def parse_server_time(pb):
    """
    Converts a Protobuf timestamp message to a UTC ``datetime.datetime``.
    """
    return pb.ToDatetime().replace(tzinfo=timezone.utc)


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
    else:
        logging.warning("Unrecognized value type for update %s", proto)
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
