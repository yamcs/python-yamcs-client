from __future__ import print_function

from yamcs.cli import utils


def list_(args):
    config = utils.read_config()
    client = utils.create_storage_client(config)
    instance = args.instance or config.get('core', 'instance')

    if args.bucket:
        listing = client.list_objects(instance, bucket_name=args.bucket)
        for obj in listing.objects:
            print(obj.name)
    else:
        for bucket in client.list_buckets(instance):
            print(bucket.name)


def mb(args):
    config = utils.read_config()
    client = utils.create_storage_client(config)
    instance = args.instance or config.get('core', 'instance')

    for bucket in args.bucket:
        client.create_bucket(instance, bucket_name=bucket)


def rb(args):
    config = utils.read_config()
    client = utils.create_storage_client(config)
    instance = args.instance or config.get('core', 'instance')

    for bucket in args.bucket:
        client.remove_bucket(instance, bucket_name=bucket)


def cat(args):
    config = utils.read_config()
    client = utils.create_storage_client(config)
    instance = args.instance or config.get('core', 'instance')

    content = client.download_object(
        instance, bucket_name=args.bucket, object_name=args.object)
    print(content)


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List buckets or objects')
    list_parser.add_argument(
        'bucket', metavar='[bucket]', type=str, nargs='?', help='bucket or object')
    list_parser.set_defaults(func=list_)

    mb_parser = subparsers.add_parser('mb', help='Make buckets')
    mb_parser.add_argument(
        'bucket', metavar='<bucket>', type=str, nargs='+', help='bucket')
    mb_parser.set_defaults(func=mb)

    rb_parser = subparsers.add_parser('rb', help='Remove buckets')
    rb_parser.add_argument(
        'bucket', metavar='<bucket>', type=str, nargs='+', help='bucket')
    rb_parser.set_defaults(func=rb)

    cat_parser = subparsers.add_parser('cat', help='Concatenate object content to stdout')
    cat_parser.add_argument('bucket', metavar='<bucket>', type=str, help='bucket')
    cat_parser.add_argument('object', metavar='<object>', type=str, help='object')
    cat_parser.set_defaults(func=cat)
