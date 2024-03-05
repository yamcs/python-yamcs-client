# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: yamcs/protobuf/activities/activities_service.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from yamcs.api import annotations_pb2 as yamcs_dot_api_dot_annotations__pb2
from yamcs.protobuf.activities import activities_pb2 as yamcs_dot_protobuf_dot_activities_dot_activities__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='yamcs/protobuf/activities/activities_service.proto',
  package='yamcs.protobuf.activities',
  syntax='proto2',
  serialized_options=b'\n\035org.yamcs.protobuf.activitiesB\026ActivitiesServiceProtoP\001',
  serialized_pb=b'\n2yamcs/protobuf/activities/activities_service.proto\x12\x19yamcs.protobuf.activities\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1byamcs/api/annotations.proto\x1a*yamcs/protobuf/activities/activities.proto\"\xd3\x01\n\x15ListActivitiesRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\r\n\x05limit\x18\x02 \x01(\x05\x12\r\n\x05order\x18\x03 \x01(\t\x12\x0e\n\x06status\x18\x04 \x03(\t\x12\x0c\n\x04type\x18\x05 \x03(\t\x12\x0c\n\x04next\x18\x06 \x01(\t\x12)\n\x05start\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12(\n\x04stop\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\t\n\x01q\x18\t \x01(\t\"8\n\x12GetActivityRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x10\n\x08\x61\x63tivity\x18\x02 \x01(\t\";\n\x15GetActivityLogRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x10\n\x08\x61\x63tivity\x18\x02 \x01(\t\"R\n\x16GetActivityLogResponse\x12\x38\n\x04logs\x18\x01 \x03(\x0b\x32*.yamcs.protobuf.activities.ActivityLogInfo\"p\n\x16ListActivitiesResponse\x12;\n\nactivities\x18\x01 \x03(\x0b\x32\'.yamcs.protobuf.activities.ActivityInfo\x12\x19\n\x11\x63ontinuationToken\x18\x02 \x01(\t\"(\n\x14ListExecutorsRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\"S\n\x15ListExecutorsResponse\x12:\n\texecutors\x18\x01 \x03(\x0b\x32\'.yamcs.protobuf.activities.ExecutorInfo\"&\n\x12ListScriptsRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\"&\n\x13ListScriptsResponse\x12\x0f\n\x07scripts\x18\x01 \x03(\t\"w\n\x14StartActivityRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12M\n\x12\x61\x63tivityDefinition\x18\x02 \x01(\x0b\x32\x31.yamcs.protobuf.activities.ActivityDefinitionInfo\";\n\x15\x43\x61ncelActivityRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x10\n\x08\x61\x63tivity\x18\x02 \x01(\t\"Z\n\x1d\x43ompleteManualActivityRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x10\n\x08\x61\x63tivity\x18\x02 \x01(\t\x12\x15\n\rfailureReason\x18\x03 \x01(\t\".\n\x1aSubscribeActivitiesRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\"A\n\x1bSubscribeActivityLogRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\x12\x10\n\x08\x61\x63tivity\x18\x02 \x01(\t\"0\n\x1cSubscribeGlobalStatusRequest\x12\x10\n\x08instance\x18\x01 \x01(\t\",\n\x14GlobalActivityStatus\x12\x14\n\x0congoingCount\x18\x01 \x01(\x05\x32\xa1\x0e\n\rActivitiesApi\x12\xa2\x01\n\x0eListActivities\x12\x30.yamcs.protobuf.activities.ListActivitiesRequest\x1a\x31.yamcs.protobuf.activities.ListActivitiesResponse\"+\x8a\x92\x03\'\n%/api/activities/{instance}/activities\x12\x9d\x01\n\x0bGetActivity\x12-.yamcs.protobuf.activities.GetActivityRequest\x1a\'.yamcs.protobuf.activities.ActivityInfo\"6\x8a\x92\x03\x32\n0/api/activities/{instance}/activities/{activity}\x12\xb1\x01\n\x0eGetActivityLog\x12\x30.yamcs.protobuf.activities.GetActivityLogRequest\x1a\x31.yamcs.protobuf.activities.GetActivityLogResponse\":\x8a\x92\x03\x36\n4/api/activities/{instance}/activities/{activity}/log\x12\xaa\x01\n\rStartActivity\x12/.yamcs.protobuf.activities.StartActivityRequest\x1a\'.yamcs.protobuf.activities.ActivityInfo\"?\x8a\x92\x03;\x1a%/api/activities/{instance}/activities:\x12\x61\x63tivityDefinition\x12\xaa\x01\n\x0e\x43\x61ncelActivity\x12\x30.yamcs.protobuf.activities.CancelActivityRequest\x1a\'.yamcs.protobuf.activities.ActivityInfo\"=\x8a\x92\x03\x39\x1a\x37/api/activities/{instance}/activities/{activity}:cancel\x12\xbf\x01\n\x16\x43ompleteManualActivity\x12\x38.yamcs.protobuf.activities.CompleteManualActivityRequest\x1a\'.yamcs.protobuf.activities.ActivityInfo\"B\x8a\x92\x03>\x1a\x39/api/activities/{instance}/activities/{activity}:complete:\x01*\x12\xa1\x01\n\x15SubscribeGlobalStatus\x12\x37.yamcs.protobuf.activities.SubscribeGlobalStatusRequest\x1a/.yamcs.protobuf.activities.GlobalActivityStatus\"\x1c\xda\x92\x03\x18\n\x16global-activity-status0\x01\x12\x89\x01\n\x13SubscribeActivities\x12\x35.yamcs.protobuf.activities.SubscribeActivitiesRequest\x1a\'.yamcs.protobuf.activities.ActivityInfo\"\x10\xda\x92\x03\x0c\n\nactivities0\x01\x12\x90\x01\n\x14SubscribeActivityLog\x12\x36.yamcs.protobuf.activities.SubscribeActivityLogRequest\x1a*.yamcs.protobuf.activities.ActivityLogInfo\"\x12\xda\x92\x03\x0e\n\x0c\x61\x63tivity-log0\x01\x12\x9e\x01\n\rListExecutors\x12/.yamcs.protobuf.activities.ListExecutorsRequest\x1a\x30.yamcs.protobuf.activities.ListExecutorsResponse\"*\x8a\x92\x03&\n$/api/activities/{instance}/executors\x12\x96\x01\n\x0bListScripts\x12-.yamcs.protobuf.activities.ListScriptsRequest\x1a..yamcs.protobuf.activities.ListScriptsResponse\"(\x8a\x92\x03$\n\"/api/activities/{instance}/scriptsB9\n\x1dorg.yamcs.protobuf.activitiesB\x16\x41\x63tivitiesServiceProtoP\x01'
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,yamcs_dot_api_dot_annotations__pb2.DESCRIPTOR,yamcs_dot_protobuf_dot_activities_dot_activities__pb2.DESCRIPTOR,])




_LISTACTIVITIESREQUEST = _descriptor.Descriptor(
  name='ListActivitiesRequest',
  full_name='yamcs.protobuf.activities.ListActivitiesRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.activities.ListActivitiesRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='limit', full_name='yamcs.protobuf.activities.ListActivitiesRequest.limit', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='order', full_name='yamcs.protobuf.activities.ListActivitiesRequest.order', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='status', full_name='yamcs.protobuf.activities.ListActivitiesRequest.status', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='type', full_name='yamcs.protobuf.activities.ListActivitiesRequest.type', index=4,
      number=5, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='next', full_name='yamcs.protobuf.activities.ListActivitiesRequest.next', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='start', full_name='yamcs.protobuf.activities.ListActivitiesRequest.start', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='stop', full_name='yamcs.protobuf.activities.ListActivitiesRequest.stop', index=7,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='q', full_name='yamcs.protobuf.activities.ListActivitiesRequest.q', index=8,
      number=9, type=9, cpp_type=9, label=1,
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
  serialized_start=188,
  serialized_end=399,
)


_GETACTIVITYREQUEST = _descriptor.Descriptor(
  name='GetActivityRequest',
  full_name='yamcs.protobuf.activities.GetActivityRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.activities.GetActivityRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='activity', full_name='yamcs.protobuf.activities.GetActivityRequest.activity', index=1,
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
  serialized_start=401,
  serialized_end=457,
)


_GETACTIVITYLOGREQUEST = _descriptor.Descriptor(
  name='GetActivityLogRequest',
  full_name='yamcs.protobuf.activities.GetActivityLogRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.activities.GetActivityLogRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='activity', full_name='yamcs.protobuf.activities.GetActivityLogRequest.activity', index=1,
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
  serialized_start=459,
  serialized_end=518,
)


_GETACTIVITYLOGRESPONSE = _descriptor.Descriptor(
  name='GetActivityLogResponse',
  full_name='yamcs.protobuf.activities.GetActivityLogResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='logs', full_name='yamcs.protobuf.activities.GetActivityLogResponse.logs', index=0,
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
  serialized_start=520,
  serialized_end=602,
)


_LISTACTIVITIESRESPONSE = _descriptor.Descriptor(
  name='ListActivitiesResponse',
  full_name='yamcs.protobuf.activities.ListActivitiesResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='activities', full_name='yamcs.protobuf.activities.ListActivitiesResponse.activities', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='continuationToken', full_name='yamcs.protobuf.activities.ListActivitiesResponse.continuationToken', index=1,
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
  serialized_start=604,
  serialized_end=716,
)


_LISTEXECUTORSREQUEST = _descriptor.Descriptor(
  name='ListExecutorsRequest',
  full_name='yamcs.protobuf.activities.ListExecutorsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.activities.ListExecutorsRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
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
  serialized_start=718,
  serialized_end=758,
)


_LISTEXECUTORSRESPONSE = _descriptor.Descriptor(
  name='ListExecutorsResponse',
  full_name='yamcs.protobuf.activities.ListExecutorsResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='executors', full_name='yamcs.protobuf.activities.ListExecutorsResponse.executors', index=0,
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
  serialized_start=760,
  serialized_end=843,
)


_LISTSCRIPTSREQUEST = _descriptor.Descriptor(
  name='ListScriptsRequest',
  full_name='yamcs.protobuf.activities.ListScriptsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.activities.ListScriptsRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
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
  serialized_start=845,
  serialized_end=883,
)


_LISTSCRIPTSRESPONSE = _descriptor.Descriptor(
  name='ListScriptsResponse',
  full_name='yamcs.protobuf.activities.ListScriptsResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='scripts', full_name='yamcs.protobuf.activities.ListScriptsResponse.scripts', index=0,
      number=1, type=9, cpp_type=9, label=3,
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
  serialized_start=885,
  serialized_end=923,
)


_STARTACTIVITYREQUEST = _descriptor.Descriptor(
  name='StartActivityRequest',
  full_name='yamcs.protobuf.activities.StartActivityRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.activities.StartActivityRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='activityDefinition', full_name='yamcs.protobuf.activities.StartActivityRequest.activityDefinition', index=1,
      number=2, type=11, cpp_type=10, label=1,
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
  serialized_start=925,
  serialized_end=1044,
)


_CANCELACTIVITYREQUEST = _descriptor.Descriptor(
  name='CancelActivityRequest',
  full_name='yamcs.protobuf.activities.CancelActivityRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.activities.CancelActivityRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='activity', full_name='yamcs.protobuf.activities.CancelActivityRequest.activity', index=1,
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
  serialized_start=1046,
  serialized_end=1105,
)


_COMPLETEMANUALACTIVITYREQUEST = _descriptor.Descriptor(
  name='CompleteManualActivityRequest',
  full_name='yamcs.protobuf.activities.CompleteManualActivityRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.activities.CompleteManualActivityRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='activity', full_name='yamcs.protobuf.activities.CompleteManualActivityRequest.activity', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='failureReason', full_name='yamcs.protobuf.activities.CompleteManualActivityRequest.failureReason', index=2,
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
  serialized_start=1107,
  serialized_end=1197,
)


_SUBSCRIBEACTIVITIESREQUEST = _descriptor.Descriptor(
  name='SubscribeActivitiesRequest',
  full_name='yamcs.protobuf.activities.SubscribeActivitiesRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.activities.SubscribeActivitiesRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
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
  serialized_start=1199,
  serialized_end=1245,
)


_SUBSCRIBEACTIVITYLOGREQUEST = _descriptor.Descriptor(
  name='SubscribeActivityLogRequest',
  full_name='yamcs.protobuf.activities.SubscribeActivityLogRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.activities.SubscribeActivityLogRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='activity', full_name='yamcs.protobuf.activities.SubscribeActivityLogRequest.activity', index=1,
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
  serialized_start=1247,
  serialized_end=1312,
)


_SUBSCRIBEGLOBALSTATUSREQUEST = _descriptor.Descriptor(
  name='SubscribeGlobalStatusRequest',
  full_name='yamcs.protobuf.activities.SubscribeGlobalStatusRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instance', full_name='yamcs.protobuf.activities.SubscribeGlobalStatusRequest.instance', index=0,
      number=1, type=9, cpp_type=9, label=1,
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
  serialized_start=1314,
  serialized_end=1362,
)


_GLOBALACTIVITYSTATUS = _descriptor.Descriptor(
  name='GlobalActivityStatus',
  full_name='yamcs.protobuf.activities.GlobalActivityStatus',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ongoingCount', full_name='yamcs.protobuf.activities.GlobalActivityStatus.ongoingCount', index=0,
      number=1, type=5, cpp_type=1, label=1,
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
  serialized_start=1364,
  serialized_end=1408,
)

_LISTACTIVITIESREQUEST.fields_by_name['start'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_LISTACTIVITIESREQUEST.fields_by_name['stop'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_GETACTIVITYLOGRESPONSE.fields_by_name['logs'].message_type = yamcs_dot_protobuf_dot_activities_dot_activities__pb2._ACTIVITYLOGINFO
_LISTACTIVITIESRESPONSE.fields_by_name['activities'].message_type = yamcs_dot_protobuf_dot_activities_dot_activities__pb2._ACTIVITYINFO
_LISTEXECUTORSRESPONSE.fields_by_name['executors'].message_type = yamcs_dot_protobuf_dot_activities_dot_activities__pb2._EXECUTORINFO
_STARTACTIVITYREQUEST.fields_by_name['activityDefinition'].message_type = yamcs_dot_protobuf_dot_activities_dot_activities__pb2._ACTIVITYDEFINITIONINFO
DESCRIPTOR.message_types_by_name['ListActivitiesRequest'] = _LISTACTIVITIESREQUEST
DESCRIPTOR.message_types_by_name['GetActivityRequest'] = _GETACTIVITYREQUEST
DESCRIPTOR.message_types_by_name['GetActivityLogRequest'] = _GETACTIVITYLOGREQUEST
DESCRIPTOR.message_types_by_name['GetActivityLogResponse'] = _GETACTIVITYLOGRESPONSE
DESCRIPTOR.message_types_by_name['ListActivitiesResponse'] = _LISTACTIVITIESRESPONSE
DESCRIPTOR.message_types_by_name['ListExecutorsRequest'] = _LISTEXECUTORSREQUEST
DESCRIPTOR.message_types_by_name['ListExecutorsResponse'] = _LISTEXECUTORSRESPONSE
DESCRIPTOR.message_types_by_name['ListScriptsRequest'] = _LISTSCRIPTSREQUEST
DESCRIPTOR.message_types_by_name['ListScriptsResponse'] = _LISTSCRIPTSRESPONSE
DESCRIPTOR.message_types_by_name['StartActivityRequest'] = _STARTACTIVITYREQUEST
DESCRIPTOR.message_types_by_name['CancelActivityRequest'] = _CANCELACTIVITYREQUEST
DESCRIPTOR.message_types_by_name['CompleteManualActivityRequest'] = _COMPLETEMANUALACTIVITYREQUEST
DESCRIPTOR.message_types_by_name['SubscribeActivitiesRequest'] = _SUBSCRIBEACTIVITIESREQUEST
DESCRIPTOR.message_types_by_name['SubscribeActivityLogRequest'] = _SUBSCRIBEACTIVITYLOGREQUEST
DESCRIPTOR.message_types_by_name['SubscribeGlobalStatusRequest'] = _SUBSCRIBEGLOBALSTATUSREQUEST
DESCRIPTOR.message_types_by_name['GlobalActivityStatus'] = _GLOBALACTIVITYSTATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ListActivitiesRequest = _reflection.GeneratedProtocolMessageType('ListActivitiesRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTACTIVITIESREQUEST,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.ListActivitiesRequest)
  })
_sym_db.RegisterMessage(ListActivitiesRequest)

GetActivityRequest = _reflection.GeneratedProtocolMessageType('GetActivityRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETACTIVITYREQUEST,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.GetActivityRequest)
  })
_sym_db.RegisterMessage(GetActivityRequest)

GetActivityLogRequest = _reflection.GeneratedProtocolMessageType('GetActivityLogRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETACTIVITYLOGREQUEST,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.GetActivityLogRequest)
  })
_sym_db.RegisterMessage(GetActivityLogRequest)

GetActivityLogResponse = _reflection.GeneratedProtocolMessageType('GetActivityLogResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETACTIVITYLOGRESPONSE,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.GetActivityLogResponse)
  })
_sym_db.RegisterMessage(GetActivityLogResponse)

ListActivitiesResponse = _reflection.GeneratedProtocolMessageType('ListActivitiesResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTACTIVITIESRESPONSE,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.ListActivitiesResponse)
  })
_sym_db.RegisterMessage(ListActivitiesResponse)

ListExecutorsRequest = _reflection.GeneratedProtocolMessageType('ListExecutorsRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTEXECUTORSREQUEST,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.ListExecutorsRequest)
  })
_sym_db.RegisterMessage(ListExecutorsRequest)

ListExecutorsResponse = _reflection.GeneratedProtocolMessageType('ListExecutorsResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTEXECUTORSRESPONSE,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.ListExecutorsResponse)
  })
_sym_db.RegisterMessage(ListExecutorsResponse)

ListScriptsRequest = _reflection.GeneratedProtocolMessageType('ListScriptsRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTSCRIPTSREQUEST,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.ListScriptsRequest)
  })
_sym_db.RegisterMessage(ListScriptsRequest)

ListScriptsResponse = _reflection.GeneratedProtocolMessageType('ListScriptsResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTSCRIPTSRESPONSE,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.ListScriptsResponse)
  })
_sym_db.RegisterMessage(ListScriptsResponse)

StartActivityRequest = _reflection.GeneratedProtocolMessageType('StartActivityRequest', (_message.Message,), {
  'DESCRIPTOR' : _STARTACTIVITYREQUEST,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.StartActivityRequest)
  })
_sym_db.RegisterMessage(StartActivityRequest)

CancelActivityRequest = _reflection.GeneratedProtocolMessageType('CancelActivityRequest', (_message.Message,), {
  'DESCRIPTOR' : _CANCELACTIVITYREQUEST,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.CancelActivityRequest)
  })
_sym_db.RegisterMessage(CancelActivityRequest)

CompleteManualActivityRequest = _reflection.GeneratedProtocolMessageType('CompleteManualActivityRequest', (_message.Message,), {
  'DESCRIPTOR' : _COMPLETEMANUALACTIVITYREQUEST,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.CompleteManualActivityRequest)
  })
_sym_db.RegisterMessage(CompleteManualActivityRequest)

SubscribeActivitiesRequest = _reflection.GeneratedProtocolMessageType('SubscribeActivitiesRequest', (_message.Message,), {
  'DESCRIPTOR' : _SUBSCRIBEACTIVITIESREQUEST,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.SubscribeActivitiesRequest)
  })
_sym_db.RegisterMessage(SubscribeActivitiesRequest)

SubscribeActivityLogRequest = _reflection.GeneratedProtocolMessageType('SubscribeActivityLogRequest', (_message.Message,), {
  'DESCRIPTOR' : _SUBSCRIBEACTIVITYLOGREQUEST,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.SubscribeActivityLogRequest)
  })
_sym_db.RegisterMessage(SubscribeActivityLogRequest)

SubscribeGlobalStatusRequest = _reflection.GeneratedProtocolMessageType('SubscribeGlobalStatusRequest', (_message.Message,), {
  'DESCRIPTOR' : _SUBSCRIBEGLOBALSTATUSREQUEST,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.SubscribeGlobalStatusRequest)
  })
_sym_db.RegisterMessage(SubscribeGlobalStatusRequest)

GlobalActivityStatus = _reflection.GeneratedProtocolMessageType('GlobalActivityStatus', (_message.Message,), {
  'DESCRIPTOR' : _GLOBALACTIVITYSTATUS,
  '__module__' : 'yamcs.protobuf.activities.activities_service_pb2'
  # @@protoc_insertion_point(class_scope:yamcs.protobuf.activities.GlobalActivityStatus)
  })
_sym_db.RegisterMessage(GlobalActivityStatus)


DESCRIPTOR._options = None

_ACTIVITIESAPI = _descriptor.ServiceDescriptor(
  name='ActivitiesApi',
  full_name='yamcs.protobuf.activities.ActivitiesApi',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=1411,
  serialized_end=3236,
  methods=[
  _descriptor.MethodDescriptor(
    name='ListActivities',
    full_name='yamcs.protobuf.activities.ActivitiesApi.ListActivities',
    index=0,
    containing_service=None,
    input_type=_LISTACTIVITIESREQUEST,
    output_type=_LISTACTIVITIESRESPONSE,
    serialized_options=b'\212\222\003\'\n%/api/activities/{instance}/activities',
  ),
  _descriptor.MethodDescriptor(
    name='GetActivity',
    full_name='yamcs.protobuf.activities.ActivitiesApi.GetActivity',
    index=1,
    containing_service=None,
    input_type=_GETACTIVITYREQUEST,
    output_type=yamcs_dot_protobuf_dot_activities_dot_activities__pb2._ACTIVITYINFO,
    serialized_options=b'\212\222\0032\n0/api/activities/{instance}/activities/{activity}',
  ),
  _descriptor.MethodDescriptor(
    name='GetActivityLog',
    full_name='yamcs.protobuf.activities.ActivitiesApi.GetActivityLog',
    index=2,
    containing_service=None,
    input_type=_GETACTIVITYLOGREQUEST,
    output_type=_GETACTIVITYLOGRESPONSE,
    serialized_options=b'\212\222\0036\n4/api/activities/{instance}/activities/{activity}/log',
  ),
  _descriptor.MethodDescriptor(
    name='StartActivity',
    full_name='yamcs.protobuf.activities.ActivitiesApi.StartActivity',
    index=3,
    containing_service=None,
    input_type=_STARTACTIVITYREQUEST,
    output_type=yamcs_dot_protobuf_dot_activities_dot_activities__pb2._ACTIVITYINFO,
    serialized_options=b'\212\222\003;\032%/api/activities/{instance}/activities:\022activityDefinition',
  ),
  _descriptor.MethodDescriptor(
    name='CancelActivity',
    full_name='yamcs.protobuf.activities.ActivitiesApi.CancelActivity',
    index=4,
    containing_service=None,
    input_type=_CANCELACTIVITYREQUEST,
    output_type=yamcs_dot_protobuf_dot_activities_dot_activities__pb2._ACTIVITYINFO,
    serialized_options=b'\212\222\0039\0327/api/activities/{instance}/activities/{activity}:cancel',
  ),
  _descriptor.MethodDescriptor(
    name='CompleteManualActivity',
    full_name='yamcs.protobuf.activities.ActivitiesApi.CompleteManualActivity',
    index=5,
    containing_service=None,
    input_type=_COMPLETEMANUALACTIVITYREQUEST,
    output_type=yamcs_dot_protobuf_dot_activities_dot_activities__pb2._ACTIVITYINFO,
    serialized_options=b'\212\222\003>\0329/api/activities/{instance}/activities/{activity}:complete:\001*',
  ),
  _descriptor.MethodDescriptor(
    name='SubscribeGlobalStatus',
    full_name='yamcs.protobuf.activities.ActivitiesApi.SubscribeGlobalStatus',
    index=6,
    containing_service=None,
    input_type=_SUBSCRIBEGLOBALSTATUSREQUEST,
    output_type=_GLOBALACTIVITYSTATUS,
    serialized_options=b'\332\222\003\030\n\026global-activity-status',
  ),
  _descriptor.MethodDescriptor(
    name='SubscribeActivities',
    full_name='yamcs.protobuf.activities.ActivitiesApi.SubscribeActivities',
    index=7,
    containing_service=None,
    input_type=_SUBSCRIBEACTIVITIESREQUEST,
    output_type=yamcs_dot_protobuf_dot_activities_dot_activities__pb2._ACTIVITYINFO,
    serialized_options=b'\332\222\003\014\n\nactivities',
  ),
  _descriptor.MethodDescriptor(
    name='SubscribeActivityLog',
    full_name='yamcs.protobuf.activities.ActivitiesApi.SubscribeActivityLog',
    index=8,
    containing_service=None,
    input_type=_SUBSCRIBEACTIVITYLOGREQUEST,
    output_type=yamcs_dot_protobuf_dot_activities_dot_activities__pb2._ACTIVITYLOGINFO,
    serialized_options=b'\332\222\003\016\n\014activity-log',
  ),
  _descriptor.MethodDescriptor(
    name='ListExecutors',
    full_name='yamcs.protobuf.activities.ActivitiesApi.ListExecutors',
    index=9,
    containing_service=None,
    input_type=_LISTEXECUTORSREQUEST,
    output_type=_LISTEXECUTORSRESPONSE,
    serialized_options=b'\212\222\003&\n$/api/activities/{instance}/executors',
  ),
  _descriptor.MethodDescriptor(
    name='ListScripts',
    full_name='yamcs.protobuf.activities.ActivitiesApi.ListScripts',
    index=10,
    containing_service=None,
    input_type=_LISTSCRIPTSREQUEST,
    output_type=_LISTSCRIPTSRESPONSE,
    serialized_options=b'\212\222\003$\n\"/api/activities/{instance}/scripts',
  ),
])
_sym_db.RegisterServiceDescriptor(_ACTIVITIESAPI)

DESCRIPTOR.services_by_name['ActivitiesApi'] = _ACTIVITIESAPI

# @@protoc_insertion_point(module_scope)
