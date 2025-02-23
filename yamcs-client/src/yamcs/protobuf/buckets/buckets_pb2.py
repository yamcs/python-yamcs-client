# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: yamcs/protobuf/buckets/buckets.proto
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
    'yamcs/protobuf/buckets/buckets.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from yamcs.api import annotations_pb2 as yamcs_dot_api_dot_annotations__pb2
from yamcs.api import httpbody_pb2 as yamcs_dot_api_dot_httpbody__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n$yamcs/protobuf/buckets/buckets.proto\x12\x16yamcs.protobuf.buckets\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1byamcs/api/annotations.proto\x1a\x18yamcs/api/httpbody.proto\"9\n\x13\x43reateBucketRequest\x12\x14\n\x08instance\x18\x01 \x01(\tB\x02\x18\x01\x12\x0c\n\x04name\x18\x02 \x01(\t\"?\n\x13\x44\x65leteBucketRequest\x12\x14\n\x08instance\x18\x01 \x01(\tB\x02\x18\x01\x12\x12\n\nbucketName\x18\x02 \x01(\t\"P\n\x10GetObjectRequest\x12\x14\n\x08instance\x18\x01 \x01(\tB\x02\x18\x01\x12\x12\n\nbucketName\x18\x02 \x01(\t\x12\x12\n\nobjectName\x18\x03 \x01(\t\">\n\x14GetObjectInfoRequest\x12\x12\n\nbucketName\x18\x01 \x01(\t\x12\x12\n\nobjectName\x18\x02 \x01(\t\"S\n\x13\x44\x65leteObjectRequest\x12\x14\n\x08instance\x18\x01 \x01(\tB\x02\x18\x01\x12\x12\n\nbucketName\x18\x02 \x01(\t\x12\x12\n\nobjectName\x18\x03 \x01(\t\"v\n\x13UploadObjectRequest\x12\x14\n\x08instance\x18\x01 \x01(\tB\x02\x18\x01\x12\x12\n\nbucketName\x18\x02 \x01(\t\x12\x12\n\nobjectName\x18\x03 \x01(\t\x12!\n\x04\x64\x61ta\x18\x04 \x01(\x0b\x32\x13.yamcs.api.HttpBody\"\xdb\x01\n\nBucketInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04size\x18\x02 \x01(\x04\x12\x12\n\nnumObjects\x18\x03 \x01(\r\x12\x0f\n\x07maxSize\x18\x04 \x01(\x04\x12\x12\n\nmaxObjects\x18\x05 \x01(\r\x12+\n\x07\x63reated\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x11\n\tdirectory\x18\x07 \x01(\t\x12\x38\n\x08location\x18\x08 \x01(\x0b\x32&.yamcs.protobuf.buckets.BucketLocation\"3\n\x0e\x42ucketLocation\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\"\xdf\x01\n\nObjectInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12+\n\x07\x63reated\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x0c\n\x04size\x18\x03 \x01(\x04\x12\x42\n\x08metadata\x18\x04 \x03(\x0b\x32\x30.yamcs.protobuf.buckets.ObjectInfo.MetadataEntry\x12\x13\n\x0b\x63ontentType\x18\x05 \x01(\t\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"*\n\x12ListBucketsRequest\x12\x14\n\x08instance\x18\x01 \x01(\tB\x02\x18\x01\"<\n\x10GetBucketRequest\x12\x14\n\x08instance\x18\x01 \x01(\tB\x02\x18\x01\x12\x12\n\nbucketName\x18\x02 \x01(\t\"J\n\x13ListBucketsResponse\x12\x33\n\x07\x62uckets\x18\x01 \x03(\x0b\x32\".yamcs.protobuf.buckets.BucketInfo\"a\n\x12ListObjectsRequest\x12\x14\n\x08instance\x18\x01 \x01(\tB\x02\x18\x01\x12\x12\n\nbucketName\x18\x02 \x01(\t\x12\x11\n\tdelimiter\x18\x03 \x01(\t\x12\x0e\n\x06prefix\x18\x04 \x01(\t\"\\\n\x13ListObjectsResponse\x12\x10\n\x08prefixes\x18\x01 \x03(\t\x12\x33\n\x07objects\x18\x02 \x03(\x0b\x32\".yamcs.protobuf.buckets.ObjectInfo2\xbb\r\n\nBucketsApi\x12\x9f\x01\n\x0bListBuckets\x12*.yamcs.protobuf.buckets.ListBucketsRequest\x1a+.yamcs.protobuf.buckets.ListBucketsResponse\"7\x8a\x92\x03\x33\n\x14/api/storage/bucketsZ\x1b\n\x17/api/buckets/{instance}0\x01\x12\xac\x01\n\tGetBucket\x12(.yamcs.protobuf.buckets.GetBucketRequest\x1a\".yamcs.protobuf.buckets.BucketInfo\"Q\x8a\x92\x03M\n!/api/storage/buckets/{bucketName}Z(\n$/api/buckets/{instance}/{bucketName}0\x01\x12\x9e\x01\n\x0c\x43reateBucket\x12+.yamcs.protobuf.buckets.CreateBucketRequest\x1a\".yamcs.protobuf.buckets.BucketInfo\"=\x8a\x92\x03\x39\x1a\x14/api/storage/buckets:\x01*Z\x1e\x1a\x17/api/buckets/{instance}0\x01:\x01*\x12\xa6\x01\n\x0c\x44\x65leteBucket\x12+.yamcs.protobuf.buckets.DeleteBucketRequest\x1a\x16.google.protobuf.Empty\"Q\x8a\x92\x03M\"!/api/storage/buckets/{bucketName}Z(\"$/api/buckets/{instance}/{bucketName}0\x01\x12\xc9\x01\n\tGetObject\x12(.yamcs.protobuf.buckets.GetObjectRequest\x1a\x13.yamcs.api.HttpBody\"}\x8a\x92\x03y\n7/api/storage/buckets/{bucketName}/objects/{objectName*}Z>\n:/api/buckets/{instance}/{bucketName}/objects/{objectName*}0\x01\x12\xa3\x01\n\rGetObjectInfo\x12,.yamcs.protobuf.buckets.GetObjectInfoRequest\x1a\".yamcs.protobuf.buckets.ObjectInfo\"@\x8a\x92\x03<\n:/api/storage/buckets/{bucketName}/objectInfo/{objectName*}\x12\xec\x01\n\x0cUploadObject\x12+.yamcs.protobuf.buckets.UploadObjectRequest\x1a\x16.google.protobuf.Empty\"\x96\x01\x8a\x92\x03\x91\x01\x1a\x38/api/storage/buckets/{bucketName}/objects/{objectName**}:\x04\x64\x61ta@\x80\x80\xc0\x02ZJ\x1a;/api/buckets/{instance}/{bucketName}/objects/{objectName**}0\x01:\x04\x64\x61ta@\x80\x80\xc0\x02\x12\xdb\x01\n\x0bListObjects\x12*.yamcs.protobuf.buckets.ListObjectsRequest\x1a+.yamcs.protobuf.buckets.ListObjectsResponse\"s\x8a\x92\x03o\n)/api/storage/buckets/{bucketName}/objectsR\x07objectsZ9\n,/api/buckets/{instance}/{bucketName}/objects0\x01R\x07objects\x12\xd2\x01\n\x0c\x44\x65leteObject\x12+.yamcs.protobuf.buckets.DeleteObjectRequest\x1a\x16.google.protobuf.Empty\"}\x8a\x92\x03y\"7/api/storage/buckets/{bucketName}/objects/{objectName*}Z>\":/api/buckets/{instance}/{bucketName}/objects/{objectName*}0\x01\x42$\n\x12org.yamcs.protobufB\x0c\x42ucketsProtoP\x01')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'yamcs.protobuf.buckets.buckets_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\022org.yamcs.protobufB\014BucketsProtoP\001'
  _globals['_CREATEBUCKETREQUEST'].fields_by_name['instance']._loaded_options = None
  _globals['_CREATEBUCKETREQUEST'].fields_by_name['instance']._serialized_options = b'\030\001'
  _globals['_DELETEBUCKETREQUEST'].fields_by_name['instance']._loaded_options = None
  _globals['_DELETEBUCKETREQUEST'].fields_by_name['instance']._serialized_options = b'\030\001'
  _globals['_GETOBJECTREQUEST'].fields_by_name['instance']._loaded_options = None
  _globals['_GETOBJECTREQUEST'].fields_by_name['instance']._serialized_options = b'\030\001'
  _globals['_DELETEOBJECTREQUEST'].fields_by_name['instance']._loaded_options = None
  _globals['_DELETEOBJECTREQUEST'].fields_by_name['instance']._serialized_options = b'\030\001'
  _globals['_UPLOADOBJECTREQUEST'].fields_by_name['instance']._loaded_options = None
  _globals['_UPLOADOBJECTREQUEST'].fields_by_name['instance']._serialized_options = b'\030\001'
  _globals['_OBJECTINFO_METADATAENTRY']._loaded_options = None
  _globals['_OBJECTINFO_METADATAENTRY']._serialized_options = b'8\001'
  _globals['_LISTBUCKETSREQUEST'].fields_by_name['instance']._loaded_options = None
  _globals['_LISTBUCKETSREQUEST'].fields_by_name['instance']._serialized_options = b'\030\001'
  _globals['_GETBUCKETREQUEST'].fields_by_name['instance']._loaded_options = None
  _globals['_GETBUCKETREQUEST'].fields_by_name['instance']._serialized_options = b'\030\001'
  _globals['_LISTOBJECTSREQUEST'].fields_by_name['instance']._loaded_options = None
  _globals['_LISTOBJECTSREQUEST'].fields_by_name['instance']._serialized_options = b'\030\001'
  _globals['_BUCKETSAPI'].methods_by_name['ListBuckets']._loaded_options = None
  _globals['_BUCKETSAPI'].methods_by_name['ListBuckets']._serialized_options = b'\212\222\0033\n\024/api/storage/bucketsZ\033\n\027/api/buckets/{instance}0\001'
  _globals['_BUCKETSAPI'].methods_by_name['GetBucket']._loaded_options = None
  _globals['_BUCKETSAPI'].methods_by_name['GetBucket']._serialized_options = b'\212\222\003M\n!/api/storage/buckets/{bucketName}Z(\n$/api/buckets/{instance}/{bucketName}0\001'
  _globals['_BUCKETSAPI'].methods_by_name['CreateBucket']._loaded_options = None
  _globals['_BUCKETSAPI'].methods_by_name['CreateBucket']._serialized_options = b'\212\222\0039\032\024/api/storage/buckets:\001*Z\036\032\027/api/buckets/{instance}0\001:\001*'
  _globals['_BUCKETSAPI'].methods_by_name['DeleteBucket']._loaded_options = None
  _globals['_BUCKETSAPI'].methods_by_name['DeleteBucket']._serialized_options = b'\212\222\003M\"!/api/storage/buckets/{bucketName}Z(\"$/api/buckets/{instance}/{bucketName}0\001'
  _globals['_BUCKETSAPI'].methods_by_name['GetObject']._loaded_options = None
  _globals['_BUCKETSAPI'].methods_by_name['GetObject']._serialized_options = b'\212\222\003y\n7/api/storage/buckets/{bucketName}/objects/{objectName*}Z>\n:/api/buckets/{instance}/{bucketName}/objects/{objectName*}0\001'
  _globals['_BUCKETSAPI'].methods_by_name['GetObjectInfo']._loaded_options = None
  _globals['_BUCKETSAPI'].methods_by_name['GetObjectInfo']._serialized_options = b'\212\222\003<\n:/api/storage/buckets/{bucketName}/objectInfo/{objectName*}'
  _globals['_BUCKETSAPI'].methods_by_name['UploadObject']._loaded_options = None
  _globals['_BUCKETSAPI'].methods_by_name['UploadObject']._serialized_options = b'\212\222\003\221\001\0328/api/storage/buckets/{bucketName}/objects/{objectName**}:\004data@\200\200\300\002ZJ\032;/api/buckets/{instance}/{bucketName}/objects/{objectName**}0\001:\004data@\200\200\300\002'
  _globals['_BUCKETSAPI'].methods_by_name['ListObjects']._loaded_options = None
  _globals['_BUCKETSAPI'].methods_by_name['ListObjects']._serialized_options = b'\212\222\003o\n)/api/storage/buckets/{bucketName}/objectsR\007objectsZ9\n,/api/buckets/{instance}/{bucketName}/objects0\001R\007objects'
  _globals['_BUCKETSAPI'].methods_by_name['DeleteObject']._loaded_options = None
  _globals['_BUCKETSAPI'].methods_by_name['DeleteObject']._serialized_options = b'\212\222\003y\"7/api/storage/buckets/{bucketName}/objects/{objectName*}Z>\":/api/buckets/{instance}/{bucketName}/objects/{objectName*}0\001'
  _globals['_CREATEBUCKETREQUEST']._serialized_start=181
  _globals['_CREATEBUCKETREQUEST']._serialized_end=238
  _globals['_DELETEBUCKETREQUEST']._serialized_start=240
  _globals['_DELETEBUCKETREQUEST']._serialized_end=303
  _globals['_GETOBJECTREQUEST']._serialized_start=305
  _globals['_GETOBJECTREQUEST']._serialized_end=385
  _globals['_GETOBJECTINFOREQUEST']._serialized_start=387
  _globals['_GETOBJECTINFOREQUEST']._serialized_end=449
  _globals['_DELETEOBJECTREQUEST']._serialized_start=451
  _globals['_DELETEOBJECTREQUEST']._serialized_end=534
  _globals['_UPLOADOBJECTREQUEST']._serialized_start=536
  _globals['_UPLOADOBJECTREQUEST']._serialized_end=654
  _globals['_BUCKETINFO']._serialized_start=657
  _globals['_BUCKETINFO']._serialized_end=876
  _globals['_BUCKETLOCATION']._serialized_start=878
  _globals['_BUCKETLOCATION']._serialized_end=929
  _globals['_OBJECTINFO']._serialized_start=932
  _globals['_OBJECTINFO']._serialized_end=1155
  _globals['_OBJECTINFO_METADATAENTRY']._serialized_start=1108
  _globals['_OBJECTINFO_METADATAENTRY']._serialized_end=1155
  _globals['_LISTBUCKETSREQUEST']._serialized_start=1157
  _globals['_LISTBUCKETSREQUEST']._serialized_end=1199
  _globals['_GETBUCKETREQUEST']._serialized_start=1201
  _globals['_GETBUCKETREQUEST']._serialized_end=1261
  _globals['_LISTBUCKETSRESPONSE']._serialized_start=1263
  _globals['_LISTBUCKETSRESPONSE']._serialized_end=1337
  _globals['_LISTOBJECTSREQUEST']._serialized_start=1339
  _globals['_LISTOBJECTSREQUEST']._serialized_end=1436
  _globals['_LISTOBJECTSRESPONSE']._serialized_start=1438
  _globals['_LISTOBJECTSRESPONSE']._serialized_end=1530
  _globals['_BUCKETSAPI']._serialized_start=1533
  _globals['_BUCKETSAPI']._serialized_end=3256
# @@protoc_insertion_point(module_scope)
