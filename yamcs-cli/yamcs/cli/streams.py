from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


def list_(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    archive = client.get_archive(opts.instance)

    rows = [['NAME']]
    for stream in archive.list_streams():
        rows.append([
            stream.name,
        ])
    utils.print_table(rows)


def describe(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    archive = client.get_archive(opts.instance)
    stream = archive.get_stream(args.stream)
    print(stream._proto)  #pylint: disable=protected-access


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List algorithms')
    list_parser.set_defaults(func=list_)

    describe_parser = subparsers.add_parser('describe', help='Describe a stream')
    describe_parser.add_argument(
        'stream', metavar='<name>', type=str, help='name of the stream')
    describe_parser.set_defaults(func=describe)
