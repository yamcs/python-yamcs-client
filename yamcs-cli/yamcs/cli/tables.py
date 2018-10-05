from __future__ import division, print_function

import gzip
import os
import time
from sys import stdout

from yamcs.cli import utils
from yamcs.client import YamcsClient


def list_(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    archive = client.get_archive(opts.instance)

    rows = [['NAME']]
    for table in archive.list_tables():
        rows.append([
            table.name,
        ])
    utils.print_table(rows)


def describe(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    archive = client.get_archive(opts.instance)
    table = archive.get_table(args.table)
    print(table._proto)  #pylint: disable=protected-access


def dump(args):
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


def load(args):
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


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List tables')
    list_parser.set_defaults(func=list_)

    describe_parser = subparsers.add_parser('describe', help='Describe a table')
    describe_parser.add_argument(
        'table', metavar='<name>', type=str, help='name of the table')
    describe_parser.set_defaults(func=describe)

    dump_parser = subparsers.add_parser('dump', help='Dump tables')
    dump_parser.add_argument(
        'tables', metavar='<name>', type=str, nargs='+', help='name of the tables')
    dump_parser.set_defaults(func=dump)
    dump_parser.add_argument('-d', '--dir', type=str,
                             help='Specifies the directory where to output dump files. Defaults to current directory')

    load_parser = subparsers.add_parser('load', help='Load tables')
    load_parser.add_argument(
        'tables', metavar='<name>', type=str, nargs='+', help='name of the tables')
    load_parser.set_defaults(func=load)
    load_parser.add_argument('-d', '--dir', type=str,
                             help='Specifies the directory where to locate dump files. Defaults to current directory')
