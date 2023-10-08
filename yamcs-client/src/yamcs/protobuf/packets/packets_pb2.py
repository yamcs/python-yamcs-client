# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: yamcs/protobuf/packets/packets.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from yamcs.protobuf import yamcs_pb2 as yamcs_dot_protobuf_dot_yamcs__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='yamcs/protobuf/packets/packets.proto',
  package='yamcs.protobuf.packets',
  syntax='proto2',
  serialized_options=b'\n\022org.yamcs.protobufB\014PacketsProtoP\001',
  serialized_pb=b'\n$yamcs/protobuf/packets/packets.proto\x12\x16yamcs.protobuf.packets\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1ayamcs/protobuf/yamcs.proto\"\x8e\x02\n\x0cTmPacketData\x12\x0e\n\x06packet\x18\x02 \x02(\x0c\x12\x16\n\x0esequenceNumber\x18\x04 \x01(\x05\x12)\n\x02id\x18\x05 \x01(\x0b\x32\x1d.yamcs.protobuf.NamedObjectId\x12\x32\n\x0egenerationTime\x18\t \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x36\n\x12\x65\x61rthReceptionTime\x18\n \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x31\n\rreceptionTime\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x0c\n\x04link\x18\x0b \x01(\tB$\n\x12org.yamcs.protobufB\x0cPacketsProtoP\x01'
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,yamcs_dot_protobuf_dot_yamcs__pb2.DESCRIPTOR,])




_TMPACKETDATA = _descriptor.Descriptor(
  name='TmPacketData',
  full_name='yamcs.protobuf.packets.TmPacketData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='packet', full_name='yamcs.protobuf.packets.TmPacketData.packet', index=0,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sequenceNumber', full_name='yamcs.protobuf.packets.TmPacketData.sequenceNumber', index=1,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='id', full_name='yamcs.protobuf.packets.TmPacketData.id', index=2,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='generationTime', full_name='yamcs.protobuf.packets.TmPacketData.generationTime', index=3,
      number=9, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='earthReceptionTime', full_name='yamcs.protobuf.packets.TmPacketData.earthReceptionTime', index=4,
      number=10, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='receptionTime', full_name='yamcs.protobuf.packets.TmPacketData.receptionTime', index=5,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='link', full_name='yamcs.protobuf.packets.TmPacketData.link', index=6,
      number=11, type=9, cpp_type=9, label=1,
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
  serialized_start=126,
  serialized_end=396,
)

_TMPACKETDATA.fields_by_name['id'].message_type = yamcs_dot_protobuf_dot_yamcs__pb2._NAMEDOBJECTID
_TMPACKETDATA.fields_by_name['generationTime'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_TMPACKETDATA.fields_by_name['earthReceptionTime'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_TMPACKETDATA.fields_by_name['receptionTime'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['TmPacketData'] = _TMPACKETDATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TmPacketData = _reflection.GeneratedProtocolMessageType('TmPacketData', (_message.Message,), {
  'DESCRIPTOR' : _TMPACKETDATA,
  '__module__' : 'yamcs.protobuf.packets.packets_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.packets.TmPacketData)
  })
_sym_db.RegisterMessage(TmPacketData)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
