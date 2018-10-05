from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


def list_(args):
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


def enable(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)

    for link in args.links:
        client.edit_data_link(opts.instance, link=link, state='enabled')


def disable(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)

    for link in args.links:
        client.edit_data_link(opts.instance, link=link, state='disabled')


def describe(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    link = client.get_data_link(opts.instance, args.link)
    print(link._proto)  #pylint: disable=protected-access


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List links')
    list_parser.set_defaults(func=list_)

    enable_parser = subparsers.add_parser('enable', help='Enable a link')
    enable_parser.add_argument(
        'links', metavar='<name>', type=str, nargs='+', help='name of the link')
    enable_parser.set_defaults(func=enable)

    disable_parser = subparsers.add_parser('disable', help='Disable a link')
    disable_parser.add_argument(
        'links', metavar='<name>', type=str, nargs='+', help='name of the link')
    disable_parser.set_defaults(func=disable)

    describe_parser = subparsers.add_parser('describe', help='Describe a link')
    describe_parser.add_argument(
        'link', metavar='<name>', type=str, help='name of the link')
    describe_parser.set_defaults(func=describe)
