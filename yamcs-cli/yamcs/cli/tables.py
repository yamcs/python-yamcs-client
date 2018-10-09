from __future__ import division, print_function

import gzip
import os
import time
from sys import stdout

from yamcs.cli import utils
from yamcs.client import YamcsClient


class TablesCommand(utils.Command):

    def __init__(self, parent):
        super(TablesCommand, self).__init__(parent, 'tables', 'Read and manipulate tables')

        subparsers = self.parser.add_subparsers(title='Commands', metavar='COMMAND')

        subparser = self.create_subparser(subparsers, 'list', 'List tables')
        subparser.set_defaults(func=self.list_)

        subparser = self.create_subparser(subparsers, 'describe', 'Describe a table')
        subparser.add_argument('table', metavar='TABLE', type=str, help='name of the table')
        subparser.set_defaults(func=self.describe)

        subparser = self.create_subparser(subparsers, 'dump', 'Dump tables')
        subparser.add_argument('tables', metavar='TABLE', type=str, nargs='+', help='name of the tables')
        subparser.set_defaults(func=self.dump)
        subparser.add_argument('-d', '--dir', type=str,
                               help='Specifies the directory where to output dump files. Defaults to current directory')

        subparser = self.create_subparser(subparsers, 'load', 'Load tables')
        subparser.add_argument('tables', metavar='TABLE', type=str, nargs='+', help='name of the tables')
        subparser.set_defaults(func=self.load)
        subparser.add_argument('-d', '--dir', type=str,
                                help='Specifies the directory where to locate dump files. Defaults to current directory')

    def list_(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)
        archive = client.get_archive(opts.instance)

        rows = [['NAME']]
        for table in archive.list_tables():
            rows.append([
                table.name,
            ])
        utils.print_table(rows)

    def describe(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)
        archive = client.get_archive(opts.instance)
        table = archive.get_table(args.table)
        print(table._proto)  #pylint: disable=protected-access

    def dump(self, args):
        if args.dir:
            if not os.path.exists(args.dir):
                os.makedirs(args.dir)

        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)
        archive = client.get_archive(opts.instance)
        for table in args.tables:
            path = table + '.dump'
            if args.dir:
                path = os.path.join(args.dir, path)
            with gzip.open(path, 'wb') as f:
                size = 0
                t1 = time.time()
                for chunk in archive.dump_table(table):
                    size += f.write(chunk)
                    t2 = time.time()
                    rate = (size / 1024 / 1024) / (t2 - t1)
                    stdout.write('\r{}: {} MB/s'.format(table, round(rate, 2)))
                    stdout.flush()
                if size > 0:
                    stdout.write('\n')

    def load(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)
        archive = client.get_archive(opts.instance)
        for table in args.tables:
            path = table + '.dump'
            if args.dir:
                path = os.path.join(args.dir, path)
            with gzip.open(path, 'rb') as f:
                stdout.write(table)
                stdout.flush()
                n = archive.load_table(table, data=f)
                stdout.write('\r{}: loaded {} rows'.format(table, n))
                stdout.write('\n')
