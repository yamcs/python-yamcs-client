from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


class StreamsCommand(utils.Command):

    def __init__(self, parent):
        super(StreamsCommand, self).__init__(parent, 'streams', 'Read streams')

        subparsers = self.parser.add_subparsers(title='Commands', metavar='COMMAND')

        subparser = self.create_subparser(subparsers, 'list', 'List streams')
        subparser.set_defaults(func=self.list_)

        subparser = self.create_subparser(subparsers, 'describe', 'Describe a stream')
        subparser.add_argument('stream', metavar='STREAM', type=str, help='name of the stream')
        subparser.set_defaults(func=self.describe)

        subparser = self.create_subparser(subparsers, 'subscribe', 'Subscribe to a stream')
        subparser.add_argument('stream', metavar='STREAM', type=str, help='name of the stream')
        #subparser.add_argument('--limit', type=int, help='Maximum number of updates. Default is unlimited.')
        subparser.set_defaults(func=self.subscribe)

    def list_(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)
        archive = client.get_archive(opts.instance)

        rows = [['NAME']]
        for stream in archive.list_streams():
            rows.append([
                stream.name,
            ])
        utils.print_table(rows)

    def describe(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)
        archive = client.get_archive(opts.instance)
        stream = archive.get_stream(args.stream)
        print(stream._proto)  #pylint: disable=protected-access

    def subscribe(self, args):
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
