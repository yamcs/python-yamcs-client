from __future__ import print_function

from yamcs import storage


def list_(args):
    client = storage.Client('localhost:8090')
    if args.bucket:
        listing = client.list_objects(instance='simulator', bucket_name=args.bucket)
        for obj in listing.objects:
            print(obj.name)
    else:
        for bucket in client.list_buckets(instance='simulator'):
            print(bucket.name)


def mb(args):
    client = storage.Client('localhost:8090')
    for bucket in args.bucket:
        client.create_bucket(instance='simulator', bucket_name=bucket)


def rb(args):
    client = storage.Client('localhost:8090')
    for bucket in args.bucket:
        client.remove_bucket(instance='simulator', bucket_name=bucket)


def cat(args):
    client = storage.Client('localhost:8090')
    content = client.download_object(instance='simulator', bucket_name=args.bucket, object_name=args.object)
    print(content)


def configure_list(parser):
    parser.add_argument('bucket', metavar='[bucket]', type=str, nargs='?', help='bucket or object')
    parser.set_defaults(func=list_)


def configure_mb(parser):
    parser.add_argument('bucket', metavar='<bucket>', type=str, nargs='+', help='bucket')
    parser.set_defaults(func=mb)


def configure_rb(parser):
    parser.add_argument('bucket', metavar='<bucket>', type=str, nargs='+', help='bucket')
    parser.set_defaults(func=rb)


def configure_cat(parser):
    parser.add_argument('bucket', metavar='<bucket>', type=str, help='bucket')
    parser.add_argument('object', metavar='<object>', type=str, help='object')
    parser.set_defaults(func=cat)


def configure_parser(parser):
    # parser.set_defaults(func=list_)
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List buckets or objects')
    configure_list(list_parser)

    mb_parser = subparsers.add_parser('mb', help='Make buckets')
    configure_mb(mb_parser)

    rb_parser = subparsers.add_parser('rb', help='Remove buckets')
    configure_rb(rb_parser)

    cat_parser = subparsers.add_parser('cat', help='Concatenate object content to stdout')
    configure_cat(cat_parser)
