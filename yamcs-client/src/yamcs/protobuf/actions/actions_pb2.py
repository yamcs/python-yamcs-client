# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: yamcs/protobuf/actions/actions.proto
# Protobuf Python Version: 5.29.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    3,
    '',
    'yamcs/protobuf/actions/actions.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from yamcs.protobuf.config import config_pb2 as yamcs_dot_protobuf_dot_config_dot_config__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n$yamcs/protobuf/actions/actions.proto\x12\x16yamcs.protobuf.actions\x1a\"yamcs/protobuf/config/config.proto\"\x87\x01\n\nActionInfo\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05label\x18\x02 \x01(\t\x12\r\n\x05style\x18\x03 \x01(\t\x12\x0f\n\x07\x65nabled\x18\x04 \x01(\x08\x12\x0f\n\x07\x63hecked\x18\x05 \x01(\x08\x12-\n\x04spec\x18\x06 \x01(\x0b\x32\x1f.yamcs.protobuf.config.SpecInfoB,\n\x1aorg.yamcs.protobuf.actionsB\x0c\x41\x63tionsProtoP\x01')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'yamcs.protobuf.actions.actions_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\032org.yamcs.protobuf.actionsB\014ActionsProtoP\001'
  _globals['_ACTIONINFO']._serialized_start=101
  _globals['_ACTIONINFO']._serialized_end=236
# @@protoc_insertion_point(module_scope)
