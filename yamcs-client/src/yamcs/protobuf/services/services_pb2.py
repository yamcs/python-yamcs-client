# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: yamcs/protobuf/services/services.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='yamcs/protobuf/services/services.proto',
  package='yamcs.protobuf.services',
  syntax='proto2',
  serialized_options=b'\n\022org.yamcs.protobufB\rServicesProtoP\001',
  serialized_pb=b'\n&yamcs/protobuf/services/services.proto\x12\x17yamcs.protobuf.services\"\xb7\x01\n\x0bServiceInfo\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x34\n\x05state\x18\x03 \x01(\x0e\x32%.yamcs.protobuf.services.ServiceState\x12\x11\n\tclassName\x18\x04 \x01(\t\x12\x11\n\tprocessor\x18\x05 \x01(\t\x12\x16\n\x0e\x66\x61ilureMessage\x18\x06 \x01(\t\x12\x14\n\x0c\x66\x61ilureCause\x18\x07 \x01(\t*\\\n\x0cServiceState\x12\x07\n\x03NEW\x10\x00\x12\x0c\n\x08STARTING\x10\x01\x12\x0b\n\x07RUNNING\x10\x02\x12\x0c\n\x08STOPPING\x10\x03\x12\x0e\n\nTERMINATED\x10\x04\x12\n\n\x06\x46\x41ILED\x10\x05\x42%\n\x12org.yamcs.protobufB\rServicesProtoP\x01'
)

_SERVICESTATE = _descriptor.EnumDescriptor(
  name='ServiceState',
  full_name='yamcs.protobuf.services.ServiceState',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NEW', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STARTING', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RUNNING', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STOPPING', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TERMINATED', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FAILED', index=5, number=5,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=253,
  serialized_end=345,
)
_sym_db.RegisterEnumDescriptor(_SERVICESTATE)

ServiceState = enum_type_wrapper.EnumTypeWrapper(_SERVICESTATE)
NEW = 0
STARTING = 1
RUNNING = 2
STOPPING = 3
TERMINATED = 4
FAILED = 5



_SERVICEINFO = _descriptor.Descriptor(
  name='ServiceInfo',
  full_name='yamcs.protobuf.services.ServiceInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.services.ServiceInfo.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='name', full_name='yamcs.protobuf.services.ServiceInfo.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='state', full_name='yamcs.protobuf.services.ServiceInfo.state', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='className', full_name='yamcs.protobuf.services.ServiceInfo.className', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processor', full_name='yamcs.protobuf.services.ServiceInfo.processor', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='failureMessage', full_name='yamcs.protobuf.services.ServiceInfo.failureMessage', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='failureCause', full_name='yamcs.protobuf.services.ServiceInfo.failureCause', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
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
  serialized_start=68,
  serialized_end=251,
)

_SERVICEINFO.fields_by_name['state'].enum_type = _SERVICESTATE
DESCRIPTOR.message_types_by_name['ServiceInfo'] = _SERVICEINFO
DESCRIPTOR.enum_types_by_name['ServiceState'] = _SERVICESTATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ServiceInfo = _reflection.GeneratedProtocolMessageType('ServiceInfo', (_message.Message,), {
  'DESCRIPTOR' : _SERVICEINFO,
  '__module__' : 'yamcs.protobuf.services.services_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.services.ServiceInfo)
  })
_sym_db.RegisterMessage(ServiceInfo)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
