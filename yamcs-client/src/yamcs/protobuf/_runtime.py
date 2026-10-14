"""
Selects the protobuf runtime used by the generated ``*_pb2`` modules and
by the client code.

If an installed ``protobuf`` package is recent enough for the generated
code, it is used (``pip install yamcs-client[protobuf]``). This enables
its compiled backend, which decodes messages much faster.

Otherwise, the bundled pure-Python copy in ``yamcs.protobuf._vendor`` is
used. This avoids version conflicts with other packages that depend on
protobuf.

Set the environment variable ``YAMCS_CLIENT_PROTOBUF=vendored`` to force
use of the bundled copy.
"""

import os
import re

__all__ = [
    "RUNTIME",
    "any_pb2",
    "api_implementation",
    "builder",
    "DecodeError",
    "descriptor",
    "descriptor_pb2",
    "descriptor_pool",
    "duration_pb2",
    "empty_pb2",
    "json_format",
    "runtime_version",
    "struct_pb2",
    "symbol_database",
    "timestamp_pb2",
    "_DecodeVarint32",
    "_VarintBytes",
]

# Version of the generated *_pb2 modules (see update-proto.sh).
# The protobuf runtime must not be older than this.
GENCODE_VERSION = (7, 35, 0)


def _can_use_installed_protobuf():
    if os.environ.get("YAMCS_CLIENT_PROTOBUF") == "vendored":
        return False
    try:
        import google.protobuf
    except ImportError:
        return False
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", google.protobuf.__version__)
    if not match:
        return False
    return tuple(int(x) for x in match.groups()) >= GENCODE_VERSION


def _init_vendored():
    # The bundled copy has no compiled backend. Select the pure-Python
    # implementation explicitly, else it warns when it detects the upb
    # backend of an installed protobuf package.
    key = "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"
    previous = os.environ.get(key)
    os.environ[key] = "python"
    try:
        import yamcs.protobuf._vendor.google.protobuf.internal.api_implementation  # noqa
    finally:
        if previous is None:
            del os.environ[key]
        else:
            os.environ[key] = previous


# Needed in either case, for the varint helpers at the end of this module
_init_vendored()

if _can_use_installed_protobuf():
    RUNTIME = "installed"
    from google.protobuf import any_pb2  # noqa
    from google.protobuf import descriptor  # noqa
    from google.protobuf import descriptor_pb2  # noqa
    from google.protobuf import descriptor_pool  # noqa
    from google.protobuf import duration_pb2  # noqa
    from google.protobuf import empty_pb2  # noqa
    from google.protobuf import json_format  # noqa
    from google.protobuf import runtime_version  # noqa
    from google.protobuf import struct_pb2  # noqa
    from google.protobuf import symbol_database  # noqa
    from google.protobuf import timestamp_pb2  # noqa
    from google.protobuf.internal import api_implementation  # noqa
    from google.protobuf.internal import builder  # noqa
    from google.protobuf.message import DecodeError  # noqa
else:
    RUNTIME = "vendored"
    from yamcs.protobuf._vendor.google.protobuf import any_pb2  # noqa
    from yamcs.protobuf._vendor.google.protobuf import descriptor  # noqa
    from yamcs.protobuf._vendor.google.protobuf import descriptor_pb2  # noqa
    from yamcs.protobuf._vendor.google.protobuf import descriptor_pool  # noqa
    from yamcs.protobuf._vendor.google.protobuf import duration_pb2  # noqa
    from yamcs.protobuf._vendor.google.protobuf import empty_pb2  # noqa
    from yamcs.protobuf._vendor.google.protobuf import json_format  # noqa
    from yamcs.protobuf._vendor.google.protobuf import runtime_version  # noqa
    from yamcs.protobuf._vendor.google.protobuf import struct_pb2  # noqa
    from yamcs.protobuf._vendor.google.protobuf import symbol_database  # noqa
    from yamcs.protobuf._vendor.google.protobuf import timestamp_pb2  # noqa
    from yamcs.protobuf._vendor.google.protobuf.internal import (  # noqa
        api_implementation,
        builder,
    )
    from yamcs.protobuf._vendor.google.protobuf.message import DecodeError  # noqa

# Low-level varint helpers for delimited streams. These are private API
# of protobuf, so always take them from the bundled copy. They operate
# on plain bytes, and work with either runtime.
from yamcs.protobuf._vendor.google.protobuf.internal.decoder import (  # noqa
    _DecodeVarint32,
)
from yamcs.protobuf._vendor.google.protobuf.internal.encoder import (  # noqa
    _VarintBytes,
)
