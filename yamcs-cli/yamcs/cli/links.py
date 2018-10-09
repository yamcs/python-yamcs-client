from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


class LinksCommand(utils.Command):

    def __init__(self, parent):
        super(LinksCommand, self).__init__(parent, 'links', 'Manage data links')

        subparsers = self.parser.add_subparsers(title='Commands', metavar='COMMAND')

        subparser = self.create_subparser(subparsers, 'list', 'List data links')
        subparser.set_defaults(func=self.list_)

        subparser = self.create_subparser(subparsers, 'describe', 'Describe a link')
        subparser.add_argument('link', metavar='LINK', type=str, help='name of the link')
        subparser.set_defaults(func=self.describe)

        subparser = self.create_subparser(subparsers, 'enable', 'Enable a link')
        subparser.add_argument('links', metavar='LINK', type=str, nargs='+', help='name of the link')
        subparser.set_defaults(func=self.enable)

        subparser = self.create_subparser(subparsers, 'disable', 'Disable a link')
        subparser.add_argument('links', metavar='LINK', type=str, nargs='+', help='name of the link')
        subparser.set_defaults(func=self.disable)

    def list_(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)

        rows = [['NAME', 'CLASS', 'STATUS', 'IN', 'OUT']]
        for link in client.list_data_links(opts.instance):
            rows.append([
                link.name,
                link.class_name,
                link.status,
                link.in_count,
                link.out_count,
            ])
        utils.print_table(rows)

    def enable(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)

        for link in args.links:
            client.enable_data_link(opts.instance, link=link)

    def disable(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)

        for link in args.links:
            client.disable_data_link(opts.instance, link=link)

    def describe(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)
        link = client.get_data_link(opts.instance, args.link)
        print(link._proto)  #pylint: disable=protected-access
