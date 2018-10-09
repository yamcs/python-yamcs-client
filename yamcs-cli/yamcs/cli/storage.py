from __future__ import print_function

import os
import shutil
import tempfile

from yamcs import storage
from yamcs.cli import utils
from yamcs.core.helpers import to_isostring


class StorageCommand(utils.Command):

    def __init__(self, parent):
        super(StorageCommand, self).__init__(parent, 'storage', 'Manage object storage')

        subparsers = self.parser.add_subparsers(title='Commands', metavar='COMMAND')

        subparser = self.create_subparser(subparsers, 'ls', 'List buckets or objects')
        subparser.add_argument('bucket', metavar='BUCKET', type=str, nargs='?', help='bucket or object')
        subparser.add_argument('-l', dest='long', action='store_true', help='List in long format')
        subparser.add_argument('-r', '-R', dest='recurse', action='store_true', help='List recursively')
        subparser.set_defaults(func=self.ls)

        subparser = self.create_subparser(subparsers, 'list', 'Synonym for ls')
        subparser.add_argument('bucket', metavar='BUCKET', type=str, nargs='?', help='bucket')
        subparser.set_defaults(func=self.ls)

        subparser = self.create_subparser(subparsers, 'mb', 'Make buckets')
        subparser.add_argument('bucket', metavar='BUCKET', type=str, nargs='+', help='bucket')
        subparser.set_defaults(func=self.mb)

        subparser = self.create_subparser(subparsers, 'rb', 'Remove buckets')
        subparser.add_argument('bucket', metavar='BUCKET', type=str, nargs='+', help='bucket')
        subparser.set_defaults(func=self.rb)

        subparser = self.create_subparser(subparsers, 'cat', 'Concatenate object content to stdout')
        subparser.add_argument('object', metavar='OBJECT', type=str, nargs='+', help='object in the format bucket://object')
        subparser.set_defaults(func=self.cat)

        subparser = self.create_subparser(subparsers, 'cp', 'Copy files or objects')
        subparser.add_argument('src', metavar='SRC', type=str, help='object in the format bucket://object')
        subparser.add_argument('dst', metavar='DST', type=str, help='object in the format bucket://object')
        subparser.set_defaults(func=self.cp)

        subparser = self.create_subparser(subparsers, 'mv', 'Move files or objects')
        subparser.add_argument('src', metavar='SRC', type=str, help='object in the format bucket://object')
        subparser.add_argument('dst', metavar='DST', type=str, help='object in the format bucket://object')
        subparser.set_defaults(func=self.mv)

        subparser = self.create_subparser(subparsers, 'rm', 'Remove objects')
        subparser.add_argument('object', metavar='OBJECT', type=str, nargs='+', help='object in the format bucket://object')
        subparser.set_defaults(func=self.rm)

    def ls(self, args):
        opts = utils.CommandOptions(args)
        client = storage.Client(**opts.client_kwargs)

        if args.bucket:
            if '://' in args.bucket:
                bucket_name, prefix = args.bucket.split('://', 1)
            else:
                bucket_name = args.bucket
                prefix = None

            delimiter = '/'
            if args.recurse:
                delimiter = None

            listing = client.list_objects(opts.instance, bucket_name=bucket_name,
                                          delimiter=delimiter, prefix=prefix)
            rows = []
            for prefix in listing.prefixes:
                url = '{}://{}'.format(bucket_name, prefix)
                if args.long:
                    rows.append(['0', '', url])
                else:
                    rows.append([url])

            for obj in listing.objects:
                url = '{}://{}'.format(bucket_name, obj.name)
                if args.long:
                    rows.append([str(obj.size), to_isostring(obj.created), url])
                else:
                    rows.append([url])

            utils.print_table(rows)
        else:
            for bucket in client.list_buckets(opts.instance):
                print(bucket.name)

    def mb(self, args):
        opts = utils.CommandOptions(args)
        client = storage.Client(**opts.client_kwargs)

        for bucket in args.bucket:
            client.create_bucket(opts.instance, bucket_name=bucket)

    def rb(self, args):
        opts = utils.CommandOptions(args)
        client = storage.Client(**opts.client_kwargs)

        for bucket in args.bucket:
            client.remove_bucket(opts.instance, bucket_name=bucket)

    def rm(self, args):
        opts = utils.CommandOptions(args)
        client = storage.Client(**opts.client_kwargs)

        for obj in args.object:
            if '://' not in obj:
                print('*** specify objects in the format bucket://object')
                return False

            parts = obj.split('://', 1)
            client.remove_object(
                opts.instance, bucket_name=parts[0], object_name=parts[1])

    def cat(self, args):
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

    def mv(self, args):
        opts = utils.CommandOptions(args)
        client = storage.Client(**opts.client_kwargs)

        if self.cp(args) is not False:
            if '://' in args.src:
                parts = args.src.split('://', 1)
                client.remove_object(
                    opts.instance, bucket_name=parts[0], object_name=parts[1])
            else:
                os.remove(args.src)

    def cp(self, args):
        opts = utils.CommandOptions(args)
        if '://' in args.src:
            if '://' in args.dst:
                return self._cp_object_to_object(opts, args.src, args.dst)
            else:
                return self._cp_object_to_file(opts, args.src, args.dst)
        else:
            if '://' in args.dst:
                return self._cp_file_to_object(opts, args.src, args.dst)
            else:
                shutil.copy(args.src, args.dst)

    def _cp_object_to_object(self, opts, src, dst):
        fd, path = tempfile.mkstemp()
        try:
            self._cp_object_to_file(opts, src, path)
            self._cp_file_to_object(opts, path, dst)
        finally:
            os.close(fd)
            os.remove(path)

    def _cp_object_to_file(self, opts, src, dst):
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

    def _cp_file_to_object(self, opts, src, dst):
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
