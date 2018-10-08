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


def subscribe(args):
    def on_data(stream_data):
        print(stream_data._proto)  #pylint: disable=protected-access

    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    archive = client.get_archive(opts.instance)
    try:
        subscription = archive.create_stream_subscription(args.stream, on_data=on_data)
        subscription.result()
    except KeyboardInterrupt:
        pass


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List algorithms')
    list_parser.set_defaults(func=list_)

    describe_parser = subparsers.add_parser('describe', help='Describe a stream')
    describe_parser.add_argument(
        'stream', metavar='<name>', type=str, help='name of the stream')
    describe_parser.set_defaults(func=describe)

    subscribe_parser = subparsers.add_parser('subscribe', help='Subscribe to a stream')
    subscribe_parser.add_argument(
        'stream', metavar='<name>', type=str, help='name of the stream')
    #subscribe_parser.add_argument(
    #    '--limit', type=int, help='Maximum number of updates. Default is unlimited.'
    #)
    subscribe_parser.set_defaults(func=subscribe)
