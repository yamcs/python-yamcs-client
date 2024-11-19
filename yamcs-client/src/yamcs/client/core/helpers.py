import binascii
import collections
import json
import logging
import os
from datetime import datetime, timezone
from threading import Timer
from typing import Any, Callable, Iterator, List, Union
from urllib.parse import urlparse

import requests
import urllib3
from google.protobuf import timestamp_pb2
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _VarintBytes
from yamcs.client.core.exceptions import ConnectionFailure, YamcsError
from yamcs.protobuf import yamcs_pb2

__all__ = [
    "adapt_name_for_rest",
    "delimit_protobuf",
    "do_get",
    "do_post",
    "do_request",
    "FixedDelay",
    "parse_server_time",
    "parse_server_timestring",
    "parse_value",
    "ProtoList",
    "split_protobuf_stream",
    "to_argument_value",
    "to_isostring",
    "to_named_object_id",
    "to_named_object_ids",
    "to_server_time",
]

logger = logging.getLogger("yamcs-client")


def to_isostring(dt: datetime) -> str:
    """
    Converts the given datetime to an ISO String for use as URL parameter.
    """
    pb = to_server_time(dt)
    return pb.ToJsonString()


def to_server_time(dt: datetime) -> timestamp_pb2.Timestamp:
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


def parse_server_timestring(isostring: str) -> datetime:
    """
    Converts an ISO string to a timezone-aware ``datetime.datetime``.
    The timezone uses the system-default. This can be overriden to UTC
    by setting the environment variable ``PYTHON_YAMCS_CLIENT_UTC``.
    """
    isostring = isostring.replace("Z", "GMT")
    try:
        naive = datetime.strptime(isostring, "%Y-%m-%dT%H:%M:%S.%f%Z")
    except ValueError:
        # Protobuf's ToJsonString does not emit fractional digits if 0
        naive = datetime.strptime(isostring, "%Y-%m-%dT%H:%M:%S%Z")
    utctime = naive.replace(tzinfo=timezone.utc)

    if os.environ.get("PYTHON_YAMCS_CLIENT_UTC") not in (None, "0"):
        return utctime
    return utctime.astimezone(tz=None)


def parse_server_time(pb: timestamp_pb2.Timestamp) -> datetime:
    """
    Converts a Protobuf timestamp message to a timezone-aware ``datetime.datetime``.
    The timezone uses the system-default. This can be overriden to UTC by setting
    the environment variable ``PYTHON_YAMCS_CLIENT_UTC``.
    """
    utctime = pb.ToDatetime().replace(tzinfo=timezone.utc)

    if os.environ.get("PYTHON_YAMCS_CLIENT_UTC") not in (None, "0"):
        return utctime
    return utctime.astimezone(tz=None)


def parse_value(proto: yamcs_pb2.Value) -> Any:
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
        return dict(map(lambda x: (x[0], parse_value(x[1])), tuples))
    elif proto.type == yamcs_pb2.Value.NONE:
        return None
    else:
        logger.warning("Unrecognized value type for update %s", proto)
        return None


def adapt_name_for_rest(name: str) -> str:
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


def to_named_object_id(parameter: str) -> yamcs_pb2.NamedObjectId:
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


def to_named_object_ids(
    parameters: Union[str, List[str]]
) -> List[yamcs_pb2.NamedObjectId]:
    """Builds a list of NamedObjectId."""
    if isinstance(parameters, str):
        return [to_named_object_id(parameters)]
    return [to_named_object_id(parameter) for parameter in parameters]


def to_argument_value(value, force_string):
    if isinstance(value, (bytes, bytearray)):
        return binascii.hexlify(value).decode("ascii")
    elif isinstance(value, str):
        return value
    elif isinstance(value, collections.abc.Mapping):
        # Careful to do the JSON dump only at the end,
        # and not at every level of a nested hierarchy
        obj = _compose_aggregate_members(value)
        return json.dumps(obj)
    elif isinstance(value, collections.abc.Sequence):
        # Yamcs expects a JSON encoded array, where elements are
        # themselves JSON-encoded (to be improved in a future version).
        obj = [to_argument_value(x, force_string=True) for x in value]
        return json.dumps(obj)
    elif isinstance(value, datetime):
        return to_isostring(value)
    elif force_string:
        return str(value)
    else:
        return value


def _compose_aggregate_members(value):
    """
    Recursively creates an object that can eventually be serialized to a valid
    aggregate value in JSON. This is a bit different than non-aggregate values,
    because Yamcs is more strict in the values that it accepts (for example:
    unlike regular arguments you cannot assign a numeric string to an integer
    argument, the JSON type needs to be numeric too).
    """
    if isinstance(value, (bytes, bytearray)):
        return binascii.hexlify(value).decode("ascii")
    elif isinstance(value, collections.abc.Mapping):
        return {k: _compose_aggregate_members(v) for k, v in value.items()}
    elif isinstance(value, datetime):
        return to_isostring(value)
    else:
        # No string conversion here, use whatever the user is giving
        return value


def do_get(session: requests.Session, path: str, **kwargs) -> requests.Response:
    """
    Performs an HTTP GET request while reraising connection-type exceptions
    to something produced by this library.
    """
    return do_request(session, "get", path, **kwargs)


def do_post(session: requests.Session, path: str, **kwargs) -> requests.Response:
    """
    Performs an HTTP POST request while reraising connection-type exceptions
    to something produced by this library.
    """
    return do_request(session, "post", path, **kwargs)


def do_request(
    session: requests.Session, method: str, path: str, **kwargs
) -> requests.Response:
    """
    Performs an HTTP request while reraising connection-type exceptions
    to something produced by this library.
    """
    try:
        session.request
        return session.request(method, path, **kwargs)
    except requests.exceptions.SSLError as ssl_error:
        url_parts = urlparse(path)
        base_url = f"{url_parts.scheme}://{url_parts.netloc}"
        msg = f"Connection to {base_url} failed: {ssl_error}"
        raise ConnectionFailure(msg) from None
    except requests.exceptions.ConnectionError as e:
        url_parts = urlparse(path)
        base_url = f"{url_parts.scheme}://{url_parts.netloc}"

        # Requests gives us a very confusing error when a connection
        # is refused. Confirm and unwrap.
        if e.args and isinstance(e.args[0], urllib3.exceptions.MaxRetryError):
            # This is a string (which is still confusing ....)
            msg = e.args[0].args[0]
            if "refused" in msg:
                msg = f"Connection to {base_url} failed: connection refused"
                raise ConnectionFailure(msg) from None
            elif "not known" in msg:
                msg = f"Connection to {base_url} failed: could not resolve hostname"
                raise ConnectionFailure(msg) from None

        raise ConnectionFailure(f"Connection to {base_url} failed: {e}")


def delimit_protobuf(message_generator: Iterator[Any], chunk_size: int = 32 * 1024):
    buf = None
    for message in message_generator:
        msg_buf = _VarintBytes(message.ByteSize()) + message.SerializeToString()
        if buf is None:
            buf = msg_buf
        else:
            buf += msg_buf
        # Not exact, use the chunk size as a treshold
        if len(buf) >= chunk_size:
            yield buf
            buf = None

    if buf:
        yield buf


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


class FixedDelay:
    """
    Helper class to run a periodic action, with a fixed delay between
    the termination of one execution, and the commencement of the next.
    """

    def __init__(
        self,
        action: Callable[[], None],
        initial_delay: float,
        period: float,
    ):
        self._timer = None
        self.action = action
        self.period = period
        self.is_running = False
        self.start(initial_delay)

    def start(self, period):
        if not self.is_running:
            self._timer = Timer(period, self._run)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self._timer:
            self._timer.cancel()
        self.is_running = False

    def _run(self):
        self.is_running = False
        self.start(self.period)
        self.action()
