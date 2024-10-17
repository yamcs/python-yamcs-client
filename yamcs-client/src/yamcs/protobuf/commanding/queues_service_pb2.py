# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: yamcs/protobuf/commanding/queues_service.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from yamcs.api import annotations_pb2 as yamcs_dot_api_dot_annotations__pb2
from yamcs.protobuf.commanding import commanding_pb2 as yamcs_dot_protobuf_dot_commanding_dot_commanding__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='yamcs/protobuf/commanding/queues_service.proto',
  package='yamcs.protobuf.commanding',
  syntax='proto2',
  serialized_options=b'\n\022org.yamcs.protobufB\022QueuesServiceProtoP\001',
  serialized_pb=b'\n.yamcs/protobuf/commanding/queues_service.proto\x12\x19yamcs.protobuf.commanding\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1byamcs/api/annotations.proto\x1a*yamcs/protobuf/commanding/commanding.proto\"8\n\x11ListQueuesRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x11\n\tprocessor\x18\x02 \x01(\t\"Q\n\x12ListQueuesResponse\x12;\n\x06queues\x18\x01 \x03(\x0b\x32+.yamcs.protobuf.commanding.CommandQueueInfo\"F\n\x1fSubscribeQueueStatisticsRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x11\n\tprocessor\x18\x02 \x01(\t\"B\n\x1bSubscribeQueueEventsRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x11\n\tprocessor\x18\x02 \x01(\t\"E\n\x0fGetQueueRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x11\n\tprocessor\x18\x02 \x01(\t\x12\r\n\x05queue\x18\x03 \x01(\t\"H\n\x12\x45nableQueueRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x11\n\tprocessor\x18\x02 \x01(\t\x12\r\n\x05queue\x18\x03 \x01(\t\"I\n\x13\x44isableQueueRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x11\n\tprocessor\x18\x02 \x01(\t\x12\r\n\x05queue\x18\x03 \x01(\t\"G\n\x11\x42lockQueueRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x11\n\tprocessor\x18\x02 \x01(\t\x12\r\n\x05queue\x18\x03 \x01(\t\"O\n\x19ListQueuedCommandsRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x11\n\tprocessor\x18\x02 \x01(\t\x12\r\n\x05queue\x18\x03 \x01(\t\"\\\n\x1aListQueuedCommandsResponse\x12>\n\x08\x63ommands\x18\x01 \x03(\x0b\x32,.yamcs.protobuf.commanding.CommandQueueEntry\"[\n\x14\x41\x63\x63\x65ptCommandRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x11\n\tprocessor\x18\x02 \x01(\t\x12\r\n\x05queue\x18\x03 \x01(\t\x12\x0f\n\x07\x63ommand\x18\x04 \x01(\t\"[\n\x14RejectCommandRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x11\n\tprocessor\x18\x02 \x01(\t\x12\r\n\x05queue\x18\x03 \x01(\t\x12\x0f\n\x07\x63ommand\x18\x04 \x01(\t2\xa2\x0f\n\tQueuesApi\x12\x9e\x01\n\nListQueues\x12,.yamcs.protobuf.commanding.ListQueuesRequest\x1a-.yamcs.protobuf.commanding.ListQueuesResponse\"3\x8a\x92\x03/\n-/api/processors/{instance}/{processor}/queues\x12\xa0\x01\n\x08GetQueue\x12*.yamcs.protobuf.commanding.GetQueueRequest\x1a+.yamcs.protobuf.commanding.CommandQueueInfo\";\x8a\x92\x03\x37\n5/api/processors/{instance}/{processor}/queues/{queue}\x12\xe2\x01\n\x0b\x45nableQueue\x12-.yamcs.protobuf.commanding.EnableQueueRequest\x1a+.yamcs.protobuf.commanding.CommandQueueInfo\"w\x8a\x92\x03s\x1a</api/processors/{instance}/{processor}/queues/{queue}:enableb3Queue \'{queue}\' enabled for processor \'{processor}\'\x12\xe6\x01\n\x0c\x44isableQueue\x12..yamcs.protobuf.commanding.DisableQueueRequest\x1a+.yamcs.protobuf.commanding.CommandQueueInfo\"y\x8a\x92\x03u\x1a=/api/processors/{instance}/{processor}/queues/{queue}:disableb4Queue \'{queue}\' disabled for processor \'{processor}\'\x12\xdf\x01\n\nBlockQueue\x12,.yamcs.protobuf.commanding.BlockQueueRequest\x1a+.yamcs.protobuf.commanding.CommandQueueInfo\"v\x8a\x92\x03r\x1a;/api/processors/{instance}/{processor}/queues/{queue}:blockb3Queue \'{queue}\' blocked for processor \'{processor}\'\x12\x98\x01\n\x18SubscribeQueueStatistics\x12:.yamcs.protobuf.commanding.SubscribeQueueStatisticsRequest\x1a+.yamcs.protobuf.commanding.CommandQueueInfo\"\x11\xda\x92\x03\r\n\x0bqueue-stats0\x01\x12\x92\x01\n\x14SubscribeQueueEvents\x12\x36.yamcs.protobuf.commanding.SubscribeQueueEventsRequest\x1a,.yamcs.protobuf.commanding.CommandQueueEvent\"\x12\xda\x92\x03\x0e\n\x0cqueue-events0\x01\x12\x8c\x02\n\x12ListQueuedCommands\x12\x34.yamcs.protobuf.commanding.ListQueuedCommandsRequest\x1a\x35.yamcs.protobuf.commanding.ListQueuedCommandsResponse\"\x88\x01\x8a\x92\x03\x83\x01\n>/api/processors/{instance}/{processor}/queues/{queue}/commandsZA\n=/api/processors/{instance}/{processor}/queues/{queue}/entries0\x01\x12\xaf\x01\n\rAcceptCommand\x12/.yamcs.protobuf.commanding.AcceptCommandRequest\x1a\x16.google.protobuf.Empty\"U\x8a\x92\x03Q\x1aO/api/processors/{instance}/{processor}/queues/{queue}/commands/{command}:accept\x12\xaf\x01\n\rRejectCommand\x12/.yamcs.protobuf.commanding.RejectCommandRequest\x1a\x16.google.protobuf.Empty\"U\x8a\x92\x03Q\x1aO/api/processors/{instance}/{processor}/queues/{queue}/commands/{command}:rejectB*\n\x12org.yamcs.protobufB\x12QueuesServiceProtoP\x01'
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,yamcs_dot_api_dot_annotations__pb2.DESCRIPTOR,yamcs_dot_protobuf_dot_commanding_dot_commanding__pb2.DESCRIPTOR,])




_LISTQUEUESREQUEST = _descriptor.Descriptor(
  name='ListQueuesRequest',
  full_name='yamcs.protobuf.commanding.ListQueuesRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.commanding.ListQueuesRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processor', full_name='yamcs.protobuf.commanding.ListQueuesRequest.processor', index=1,
      number=2, type=9, cpp_type=9, label=1,
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
  serialized_start=179,
  serialized_end=235,
)


_LISTQUEUESRESPONSE = _descriptor.Descriptor(
  name='ListQueuesResponse',
  full_name='yamcs.protobuf.commanding.ListQueuesResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='queues', full_name='yamcs.protobuf.commanding.ListQueuesResponse.queues', index=0,
      number=1, type=11, cpp_type=10, label=3,
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
  serialized_start=237,
  serialized_end=318,
)


_SUBSCRIBEQUEUESTATISTICSREQUEST = _descriptor.Descriptor(
  name='SubscribeQueueStatisticsRequest',
  full_name='yamcs.protobuf.commanding.SubscribeQueueStatisticsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.commanding.SubscribeQueueStatisticsRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processor', full_name='yamcs.protobuf.commanding.SubscribeQueueStatisticsRequest.processor', index=1,
      number=2, type=9, cpp_type=9, label=1,
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
  serialized_start=320,
  serialized_end=390,
)


_SUBSCRIBEQUEUEEVENTSREQUEST = _descriptor.Descriptor(
  name='SubscribeQueueEventsRequest',
  full_name='yamcs.protobuf.commanding.SubscribeQueueEventsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.commanding.SubscribeQueueEventsRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processor', full_name='yamcs.protobuf.commanding.SubscribeQueueEventsRequest.processor', index=1,
      number=2, type=9, cpp_type=9, label=1,
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
  serialized_start=392,
  serialized_end=458,
)


_GETQUEUEREQUEST = _descriptor.Descriptor(
  name='GetQueueRequest',
  full_name='yamcs.protobuf.commanding.GetQueueRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.commanding.GetQueueRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processor', full_name='yamcs.protobuf.commanding.GetQueueRequest.processor', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='queue', full_name='yamcs.protobuf.commanding.GetQueueRequest.queue', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  serialized_start=460,
  serialized_end=529,
)


_ENABLEQUEUEREQUEST = _descriptor.Descriptor(
  name='EnableQueueRequest',
  full_name='yamcs.protobuf.commanding.EnableQueueRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.commanding.EnableQueueRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processor', full_name='yamcs.protobuf.commanding.EnableQueueRequest.processor', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='queue', full_name='yamcs.protobuf.commanding.EnableQueueRequest.queue', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  serialized_start=531,
  serialized_end=603,
)


_DISABLEQUEUEREQUEST = _descriptor.Descriptor(
  name='DisableQueueRequest',
  full_name='yamcs.protobuf.commanding.DisableQueueRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.commanding.DisableQueueRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processor', full_name='yamcs.protobuf.commanding.DisableQueueRequest.processor', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='queue', full_name='yamcs.protobuf.commanding.DisableQueueRequest.queue', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  serialized_start=605,
  serialized_end=678,
)


_BLOCKQUEUEREQUEST = _descriptor.Descriptor(
  name='BlockQueueRequest',
  full_name='yamcs.protobuf.commanding.BlockQueueRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.commanding.BlockQueueRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processor', full_name='yamcs.protobuf.commanding.BlockQueueRequest.processor', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='queue', full_name='yamcs.protobuf.commanding.BlockQueueRequest.queue', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  serialized_start=680,
  serialized_end=751,
)


_LISTQUEUEDCOMMANDSREQUEST = _descriptor.Descriptor(
  name='ListQueuedCommandsRequest',
  full_name='yamcs.protobuf.commanding.ListQueuedCommandsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.commanding.ListQueuedCommandsRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processor', full_name='yamcs.protobuf.commanding.ListQueuedCommandsRequest.processor', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='queue', full_name='yamcs.protobuf.commanding.ListQueuedCommandsRequest.queue', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  serialized_start=753,
  serialized_end=832,
)


_LISTQUEUEDCOMMANDSRESPONSE = _descriptor.Descriptor(
  name='ListQueuedCommandsResponse',
  full_name='yamcs.protobuf.commanding.ListQueuedCommandsResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='commands', full_name='yamcs.protobuf.commanding.ListQueuedCommandsResponse.commands', index=0,
      number=1, type=11, cpp_type=10, label=3,
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
  serialized_start=834,
  serialized_end=926,
)


_ACCEPTCOMMANDREQUEST = _descriptor.Descriptor(
  name='AcceptCommandRequest',
  full_name='yamcs.protobuf.commanding.AcceptCommandRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.commanding.AcceptCommandRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processor', full_name='yamcs.protobuf.commanding.AcceptCommandRequest.processor', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='queue', full_name='yamcs.protobuf.commanding.AcceptCommandRequest.queue', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='command', full_name='yamcs.protobuf.commanding.AcceptCommandRequest.command', index=3,
      number=4, type=9, cpp_type=9, label=1,
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
  serialized_start=928,
  serialized_end=1019,
)


_REJECTCOMMANDREQUEST = _descriptor.Descriptor(
  name='RejectCommandRequest',
  full_name='yamcs.protobuf.commanding.RejectCommandRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.commanding.RejectCommandRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processor', full_name='yamcs.protobuf.commanding.RejectCommandRequest.processor', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='queue', full_name='yamcs.protobuf.commanding.RejectCommandRequest.queue', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='command', full_name='yamcs.protobuf.commanding.RejectCommandRequest.command', index=3,
      number=4, type=9, cpp_type=9, label=1,
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
  serialized_start=1021,
  serialized_end=1112,
)

_LISTQUEUESRESPONSE.fields_by_name['queues'].message_type = yamcs_dot_protobuf_dot_commanding_dot_commanding__pb2._COMMANDQUEUEINFO
_LISTQUEUEDCOMMANDSRESPONSE.fields_by_name['commands'].message_type = yamcs_dot_protobuf_dot_commanding_dot_commanding__pb2._COMMANDQUEUEENTRY
DESCRIPTOR.message_types_by_name['ListQueuesRequest'] = _LISTQUEUESREQUEST
DESCRIPTOR.message_types_by_name['ListQueuesResponse'] = _LISTQUEUESRESPONSE
DESCRIPTOR.message_types_by_name['SubscribeQueueStatisticsRequest'] = _SUBSCRIBEQUEUESTATISTICSREQUEST
DESCRIPTOR.message_types_by_name['SubscribeQueueEventsRequest'] = _SUBSCRIBEQUEUEEVENTSREQUEST
DESCRIPTOR.message_types_by_name['GetQueueRequest'] = _GETQUEUEREQUEST
DESCRIPTOR.message_types_by_name['EnableQueueRequest'] = _ENABLEQUEUEREQUEST
DESCRIPTOR.message_types_by_name['DisableQueueRequest'] = _DISABLEQUEUEREQUEST
DESCRIPTOR.message_types_by_name['BlockQueueRequest'] = _BLOCKQUEUEREQUEST
DESCRIPTOR.message_types_by_name['ListQueuedCommandsRequest'] = _LISTQUEUEDCOMMANDSREQUEST
DESCRIPTOR.message_types_by_name['ListQueuedCommandsResponse'] = _LISTQUEUEDCOMMANDSRESPONSE
DESCRIPTOR.message_types_by_name['AcceptCommandRequest'] = _ACCEPTCOMMANDREQUEST
DESCRIPTOR.message_types_by_name['RejectCommandRequest'] = _REJECTCOMMANDREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ListQueuesRequest = _reflection.GeneratedProtocolMessageType('ListQueuesRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTQUEUESREQUEST,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.ListQueuesRequest)
  })
_sym_db.RegisterMessage(ListQueuesRequest)

ListQueuesResponse = _reflection.GeneratedProtocolMessageType('ListQueuesResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTQUEUESRESPONSE,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.ListQueuesResponse)
  })
_sym_db.RegisterMessage(ListQueuesResponse)

SubscribeQueueStatisticsRequest = _reflection.GeneratedProtocolMessageType('SubscribeQueueStatisticsRequest', (_message.Message,), {
  'DESCRIPTOR' : _SUBSCRIBEQUEUESTATISTICSREQUEST,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.SubscribeQueueStatisticsRequest)
  })
_sym_db.RegisterMessage(SubscribeQueueStatisticsRequest)

SubscribeQueueEventsRequest = _reflection.GeneratedProtocolMessageType('SubscribeQueueEventsRequest', (_message.Message,), {
  'DESCRIPTOR' : _SUBSCRIBEQUEUEEVENTSREQUEST,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.SubscribeQueueEventsRequest)
  })
_sym_db.RegisterMessage(SubscribeQueueEventsRequest)

GetQueueRequest = _reflection.GeneratedProtocolMessageType('GetQueueRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETQUEUEREQUEST,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.GetQueueRequest)
  })
_sym_db.RegisterMessage(GetQueueRequest)

EnableQueueRequest = _reflection.GeneratedProtocolMessageType('EnableQueueRequest', (_message.Message,), {
  'DESCRIPTOR' : _ENABLEQUEUEREQUEST,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.EnableQueueRequest)
  })
_sym_db.RegisterMessage(EnableQueueRequest)

DisableQueueRequest = _reflection.GeneratedProtocolMessageType('DisableQueueRequest', (_message.Message,), {
  'DESCRIPTOR' : _DISABLEQUEUEREQUEST,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.DisableQueueRequest)
  })
_sym_db.RegisterMessage(DisableQueueRequest)

BlockQueueRequest = _reflection.GeneratedProtocolMessageType('BlockQueueRequest', (_message.Message,), {
  'DESCRIPTOR' : _BLOCKQUEUEREQUEST,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.BlockQueueRequest)
  })
_sym_db.RegisterMessage(BlockQueueRequest)

ListQueuedCommandsRequest = _reflection.GeneratedProtocolMessageType('ListQueuedCommandsRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTQUEUEDCOMMANDSREQUEST,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.ListQueuedCommandsRequest)
  })
_sym_db.RegisterMessage(ListQueuedCommandsRequest)

ListQueuedCommandsResponse = _reflection.GeneratedProtocolMessageType('ListQueuedCommandsResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTQUEUEDCOMMANDSRESPONSE,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.ListQueuedCommandsResponse)
  })
_sym_db.RegisterMessage(ListQueuedCommandsResponse)

AcceptCommandRequest = _reflection.GeneratedProtocolMessageType('AcceptCommandRequest', (_message.Message,), {
  'DESCRIPTOR' : _ACCEPTCOMMANDREQUEST,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.AcceptCommandRequest)
  })
_sym_db.RegisterMessage(AcceptCommandRequest)

RejectCommandRequest = _reflection.GeneratedProtocolMessageType('RejectCommandRequest', (_message.Message,), {
  'DESCRIPTOR' : _REJECTCOMMANDREQUEST,
  '__module__' : 'yamcs.protobuf.commanding.queues_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.commanding.RejectCommandRequest)
  })
_sym_db.RegisterMessage(RejectCommandRequest)


DESCRIPTOR._options = None

_QUEUESAPI = _descriptor.ServiceDescriptor(
  name='QueuesApi',
  full_name='yamcs.protobuf.commanding.QueuesApi',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=1115,
  serialized_end=3069,
  methods=[
  _descriptor.MethodDescriptor(
    name='ListQueues',
    full_name='yamcs.protobuf.commanding.QueuesApi.ListQueues',
    index=0,
    containing_service=None,
    input_type=_LISTQUEUESREQUEST,
    output_type=_LISTQUEUESRESPONSE,
    serialized_options=b'\212\222\003/\n-/api/processors/{instance}/{processor}/queues',
  ),
  _descriptor.MethodDescriptor(
    name='GetQueue',
    full_name='yamcs.protobuf.commanding.QueuesApi.GetQueue',
    index=1,
    containing_service=None,
    input_type=_GETQUEUEREQUEST,
    output_type=yamcs_dot_protobuf_dot_commanding_dot_commanding__pb2._COMMANDQUEUEINFO,
    serialized_options=b'\212\222\0037\n5/api/processors/{instance}/{processor}/queues/{queue}',
  ),
  _descriptor.MethodDescriptor(
    name='EnableQueue',
    full_name='yamcs.protobuf.commanding.QueuesApi.EnableQueue',
    index=2,
    containing_service=None,
    input_type=_ENABLEQUEUEREQUEST,
    output_type=yamcs_dot_protobuf_dot_commanding_dot_commanding__pb2._COMMANDQUEUEINFO,
    serialized_options=b'\212\222\003s\032</api/processors/{instance}/{processor}/queues/{queue}:enableb3Queue \'{queue}\' enabled for processor \'{processor}\'',
  ),
  _descriptor.MethodDescriptor(
    name='DisableQueue',
    full_name='yamcs.protobuf.commanding.QueuesApi.DisableQueue',
    index=3,
    containing_service=None,
    input_type=_DISABLEQUEUEREQUEST,
    output_type=yamcs_dot_protobuf_dot_commanding_dot_commanding__pb2._COMMANDQUEUEINFO,
    serialized_options=b'\212\222\003u\032=/api/processors/{instance}/{processor}/queues/{queue}:disableb4Queue \'{queue}\' disabled for processor \'{processor}\'',
  ),
  _descriptor.MethodDescriptor(
    name='BlockQueue',
    full_name='yamcs.protobuf.commanding.QueuesApi.BlockQueue',
    index=4,
    containing_service=None,
    input_type=_BLOCKQUEUEREQUEST,
    output_type=yamcs_dot_protobuf_dot_commanding_dot_commanding__pb2._COMMANDQUEUEINFO,
    serialized_options=b'\212\222\003r\032;/api/processors/{instance}/{processor}/queues/{queue}:blockb3Queue \'{queue}\' blocked for processor \'{processor}\'',
  ),
  _descriptor.MethodDescriptor(
    name='SubscribeQueueStatistics',
    full_name='yamcs.protobuf.commanding.QueuesApi.SubscribeQueueStatistics',
    index=5,
    containing_service=None,
    input_type=_SUBSCRIBEQUEUESTATISTICSREQUEST,
    output_type=yamcs_dot_protobuf_dot_commanding_dot_commanding__pb2._COMMANDQUEUEINFO,
    serialized_options=b'\332\222\003\r\n\013queue-stats',
  ),
  _descriptor.MethodDescriptor(
    name='SubscribeQueueEvents',
    full_name='yamcs.protobuf.commanding.QueuesApi.SubscribeQueueEvents',
    index=6,
    containing_service=None,
    input_type=_SUBSCRIBEQUEUEEVENTSREQUEST,
    output_type=yamcs_dot_protobuf_dot_commanding_dot_commanding__pb2._COMMANDQUEUEEVENT,
    serialized_options=b'\332\222\003\016\n\014queue-events',
  ),
  _descriptor.MethodDescriptor(
    name='ListQueuedCommands',
    full_name='yamcs.protobuf.commanding.QueuesApi.ListQueuedCommands',
    index=7,
    containing_service=None,
    input_type=_LISTQUEUEDCOMMANDSREQUEST,
    output_type=_LISTQUEUEDCOMMANDSRESPONSE,
    serialized_options=b'\212\222\003\203\001\n>/api/processors/{instance}/{processor}/queues/{queue}/commandsZA\n=/api/processors/{instance}/{processor}/queues/{queue}/entries0\001',
  ),
  _descriptor.MethodDescriptor(
    name='AcceptCommand',
    full_name='yamcs.protobuf.commanding.QueuesApi.AcceptCommand',
    index=8,
    containing_service=None,
    input_type=_ACCEPTCOMMANDREQUEST,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    serialized_options=b'\212\222\003Q\032O/api/processors/{instance}/{processor}/queues/{queue}/commands/{command}:accept',
  ),
  _descriptor.MethodDescriptor(
    name='RejectCommand',
    full_name='yamcs.protobuf.commanding.QueuesApi.RejectCommand',
    index=9,
    containing_service=None,
    input_type=_REJECTCOMMANDREQUEST,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    serialized_options=b'\212\222\003Q\032O/api/processors/{instance}/{processor}/queues/{queue}/commands/{command}:reject',
  ),
])
_sym_db.RegisterServiceDescriptor(_QUEUESAPI)

DESCRIPTOR.services_by_name['QueuesApi'] = _QUEUESAPI

# @@protoc_insertion_point(module_scope)
