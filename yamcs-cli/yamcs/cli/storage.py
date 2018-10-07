from __future__ import print_function

import os
import shutil
import tempfile

from yamcs import storage
from yamcs.cli import utils


def ls(args):
    opts = utils.CommandOptions(args)
    client = storage.Client(**opts.client_kwargs)

    if args.bucket:
        if '://' in args.bucket:
            bucket_name, object_name = args.bucket.split('://', 1)
        else:
            bucket_name = args.bucket
            object_name = None

        listing = client.list_objects(opts.instance, bucket_name=bucket_name,
                                      delimiter='/', prefix=object_name)
        for prefix in listing.prefixes:
            print('{}://{}'.format(bucket_name, prefix))
        for obj in listing.objects:
            print('{}://{}'.format(bucket_name, obj.name))
    else:
        for bucket in client.list_buckets(opts.instance):
            print(bucket.name)


def mb(args):
    opts = utils.CommandOptions(args)
    client = storage.Client(**opts.client_kwargs)

    for bucket in args.bucket:
        client.create_bucket(opts.instance, bucket_name=bucket)


def rb(args):
    opts = utils.CommandOptions(args)
    client = storage.Client(**opts.client_kwargs)

    for bucket in args.bucket:
        client.remove_bucket(opts.instance, bucket_name=bucket)


def cat(args):
    opts = utils.CommandOptions(args)
    client = storage.Client(**opts.client_kwargs)

    for obj in args.object:
        if '://' not in obj:
            print('*** specify objects in the format bucket://object')
            return False

        parts = obj.split('://', 1)

        content = client.download_object(
            opts.instance, bucket_name=parts[0], object_name=parts[1])
        print(content)


def mv(args):
    opts = utils.CommandOptions(args)
    client = storage.Client(**opts.client_kwargs)

    if cp(args) is not False:
        if '://' in args.src:
            parts = args.src.split('://', 1)
            client.remove_object(
                opts.instance, bucket_name=parts[0], object_name=parts[1])
        else:
            os.remove(args.src)


def cp(args):
    opts = utils.CommandOptions(args)
    if '://' in args.src:
        if '://' in args.dst:
            return _cp_object_to_object(opts, args.src, args.dst)
        else:
            return _cp_object_to_file(opts, args.src, args.dst)
    else:
        if '://' in args.dst:
            return _cp_file_to_object(opts, args.src, args.dst)
        else:
            shutil.copy(args.src, args.dst)


def _cp_object_to_object(opts, src, dst):
    fd, path = tempfile.mkstemp()
    try:
        _cp_object_to_file(opts, src, path)
        _cp_file_to_object(opts, path, dst)
    finally:
        os.close(fd)
        os.remove(path)


def _cp_object_to_file(opts, src, dst):
    parts = src.split('://', 1)
    src_bucket = parts[0]
    src_object = parts[1]
    _, src_filename = os.path.split(src_object)

    client = storage.Client(**opts.client_kwargs)
    content = client.download_object(
        opts.instance, bucket_name=src_bucket, object_name=src_object)

    if os.path.isdir(dst):
        target_file = os.path.join(dst, src_filename)
    else:
        target_file = dst

    with open(target_file, 'wb') as f:
        f.write(content)


def _cp_file_to_object(opts, src, dst):
    if os.path.isdir(src):
        print('*** {} is a directory'.format(src))
        return False

    parts = dst.split('://', 1)
    dst_bucket = parts[0]
    if len(parts) > 1:
        dst_object = parts[1]
    else:
        _, dst_object = os.path.split(src)

    client = storage.Client(**opts.client_kwargs)
    client.upload_object(
        opts.instance, bucket_name=dst_bucket, object_name=dst_object, file_obj=src)


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    ls_parser = subparsers.add_parser('ls', help='List buckets or objects')
    ls_parser.add_argument(
        'bucket', metavar='[bucket]', type=str, nargs='?', help='bucket or object')
    ls_parser.set_defaults(func=ls)

    list_parser = subparsers.add_parser('list', help='Synonym for ls')
    list_parser.add_argument(
        'bucket', metavar='[bucket]', type=str, nargs='?', help='bucket')
    list_parser.set_defaults(func=ls)

    mb_parser = subparsers.add_parser('mb', help='Make buckets')
    mb_parser.add_argument(
        'bucket', metavar='<bucket>', type=str, nargs='+', help='bucket')
    mb_parser.set_defaults(func=mb)

    rb_parser = subparsers.add_parser('rb', help='Remove buckets')
    rb_parser.add_argument(
        'bucket', metavar='<bucket>', type=str, nargs='+', help='bucket')
    rb_parser.set_defaults(func=rb)

    cat_parser = subparsers.add_parser('cat', help='Concatenate object content to stdout')
    cat_parser.add_argument('object', metavar='<object>', type=str, nargs='+',
                            help='object in the format bucket://object')
    cat_parser.set_defaults(func=cat)

    cp_parser = subparsers.add_parser('cp', help='Copy files or objects')
    cp_parser.add_argument('src', metavar='src', type=str,
                           help='object in the format bucket://object')
    cp_parser.add_argument('dst', metavar='dst', type=str,
                           help='object in the format bucket://object')
    cp_parser.set_defaults(func=cp)

    mv_parser = subparsers.add_parser('mv', help='Move files or objects')
    mv_parser.add_argument('src', metavar='src', type=str,
                           help='object in the format bucket://object')
    mv_parser.add_argument('dst', metavar='dst', type=str,
                           help='object in the format bucket://object')
    mv_parser.set_defaults(func=mv)
