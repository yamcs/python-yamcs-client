# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: yamcs/protobuf/pvalue/pvalue_service.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from yamcs.api import annotations_pb2 as yamcs_dot_api_dot_annotations__pb2
from yamcs.protobuf import yamcs_pb2 as yamcs_dot_protobuf_dot_yamcs__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='yamcs/protobuf/pvalue/pvalue_service.proto',
  package='yamcs.protobuf.pvalue',
  syntax='proto2',
  serialized_options=b'\n\022org.yamcs.protobufB\033ParameterValuesServiceProtoP\001',
  serialized_pb=b'\n*yamcs/protobuf/pvalue/pvalue_service.proto\x12\x15yamcs.protobuf.pvalue\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1byamcs/api/annotations.proto\x1a\x1ayamcs/protobuf/yamcs.proto\"{\n\x1aLoadParameterValuesRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x0e\n\x06stream\x18\x02 \x01(\t\x12;\n\x06values\x18\x03 \x03(\x0b\x32+.yamcs.protobuf.pvalue.ParameterValueUpdate\"\x9f\x01\n\x1bLoadParameterValuesResponse\x12\x12\n\nvalueCount\x18\x01 \x01(\r\x12\x35\n\x11minGenerationTime\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x35\n\x11maxGenerationTime\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x96\x01\n\x14ParameterValueUpdate\x12\x11\n\tparameter\x18\x01 \x01(\t\x12$\n\x05value\x18\x02 \x01(\x0b\x32\x15.yamcs.protobuf.Value\x12\x32\n\x0egenerationTime\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x11\n\texpiresIn\x18\x04 \x01(\x04\x32\xd6\x01\n\x12ParameterValuesApi\x12\xbf\x01\n\x13LoadParameterValues\x12\x31.yamcs.protobuf.pvalue.LoadParameterValuesRequest\x1a\x32.yamcs.protobuf.pvalue.LoadParameterValuesResponse\"?\x8a\x92\x03;\x1a\x36/api/parameter-values/{instance}/streams/{stream}:load:\x01*(\x01\x42\x33\n\x12org.yamcs.protobufB\x1bParameterValuesServiceProtoP\x01'
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,yamcs_dot_api_dot_annotations__pb2.DESCRIPTOR,yamcs_dot_protobuf_dot_yamcs__pb2.DESCRIPTOR,])




_LOADPARAMETERVALUESREQUEST = _descriptor.Descriptor(
  name='LoadParameterValuesRequest',
  full_name='yamcs.protobuf.pvalue.LoadParameterValuesRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.pvalue.LoadParameterValuesRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='stream', full_name='yamcs.protobuf.pvalue.LoadParameterValuesRequest.stream', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='values', full_name='yamcs.protobuf.pvalue.LoadParameterValuesRequest.values', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=159,
  serialized_end=282,
)


_LOADPARAMETERVALUESRESPONSE = _descriptor.Descriptor(
  name='LoadParameterValuesResponse',
  full_name='yamcs.protobuf.pvalue.LoadParameterValuesResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='valueCount', full_name='yamcs.protobuf.pvalue.LoadParameterValuesResponse.valueCount', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='minGenerationTime', full_name='yamcs.protobuf.pvalue.LoadParameterValuesResponse.minGenerationTime', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='maxGenerationTime', full_name='yamcs.protobuf.pvalue.LoadParameterValuesResponse.maxGenerationTime', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=285,
  serialized_end=444,
)


_PARAMETERVALUEUPDATE = _descriptor.Descriptor(
  name='ParameterValueUpdate',
  full_name='yamcs.protobuf.pvalue.ParameterValueUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='parameter', full_name='yamcs.protobuf.pvalue.ParameterValueUpdate.parameter', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='yamcs.protobuf.pvalue.ParameterValueUpdate.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='generationTime', full_name='yamcs.protobuf.pvalue.ParameterValueUpdate.generationTime', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='expiresIn', full_name='yamcs.protobuf.pvalue.ParameterValueUpdate.expiresIn', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=447,
  serialized_end=597,
)

_LOADPARAMETERVALUESREQUEST.fields_by_name['values'].message_type = _PARAMETERVALUEUPDATE
_LOADPARAMETERVALUESRESPONSE.fields_by_name['minGenerationTime'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_LOADPARAMETERVALUESRESPONSE.fields_by_name['maxGenerationTime'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_PARAMETERVALUEUPDATE.fields_by_name['value'].message_type = yamcs_dot_protobuf_dot_yamcs__pb2._VALUE
_PARAMETERVALUEUPDATE.fields_by_name['generationTime'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['LoadParameterValuesRequest'] = _LOADPARAMETERVALUESREQUEST
DESCRIPTOR.message_types_by_name['LoadParameterValuesResponse'] = _LOADPARAMETERVALUESRESPONSE
DESCRIPTOR.message_types_by_name['ParameterValueUpdate'] = _PARAMETERVALUEUPDATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LoadParameterValuesRequest = _reflection.GeneratedProtocolMessageType('LoadParameterValuesRequest', (_message.Message,), {
  'DESCRIPTOR' : _LOADPARAMETERVALUESREQUEST,
  '__module__' : 'yamcs.protobuf.pvalue.pvalue_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.pvalue.LoadParameterValuesRequest)
  })
_sym_db.RegisterMessage(LoadParameterValuesRequest)

LoadParameterValuesResponse = _reflection.GeneratedProtocolMessageType('LoadParameterValuesResponse', (_message.Message,), {
  'DESCRIPTOR' : _LOADPARAMETERVALUESRESPONSE,
  '__module__' : 'yamcs.protobuf.pvalue.pvalue_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.pvalue.LoadParameterValuesResponse)
  })
_sym_db.RegisterMessage(LoadParameterValuesResponse)

ParameterValueUpdate = _reflection.GeneratedProtocolMessageType('ParameterValueUpdate', (_message.Message,), {
  'DESCRIPTOR' : _PARAMETERVALUEUPDATE,
  '__module__' : 'yamcs.protobuf.pvalue.pvalue_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.pvalue.ParameterValueUpdate)
  })
_sym_db.RegisterMessage(ParameterValueUpdate)


DESCRIPTOR._options = None

_PARAMETERVALUESAPI = _descriptor.ServiceDescriptor(
  name='ParameterValuesApi',
  full_name='yamcs.protobuf.pvalue.ParameterValuesApi',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=600,
  serialized_end=814,
  methods=[
  _descriptor.MethodDescriptor(
    name='LoadParameterValues',
    full_name='yamcs.protobuf.pvalue.ParameterValuesApi.LoadParameterValues',
    index=0,
    containing_service=None,
    input_type=_LOADPARAMETERVALUESREQUEST,
    output_type=_LOADPARAMETERVALUESRESPONSE,
    serialized_options=b'\212\222\003;\0326/api/parameter-values/{instance}/streams/{stream}:load:\001*',
  ),
])
_sym_db.RegisterServiceDescriptor(_PARAMETERVALUESAPI)

DESCRIPTOR.services_by_name['ParameterValuesApi'] = _PARAMETERVALUESAPI

# @@protoc_insertion_point(module_scope)
