from __future__ import print_function

from yamcs.cli.utils import print_table
from yamcs.client import YamcsClient


def list_(args):
    client = YamcsClient('localhost:8090')

    rows = [['NAME', 'CLASS', 'STATUS', 'IN', 'OUT']]
    for link in client.list_data_links(instance='simulator'):
        rows.append([
            link.name,
            link.class_name,
            link.status,
            link.in_count,
            link.out_count,
        ])
    print_table(rows)


def enable(args):
    client = YamcsClient('localhost:8090')
    for link in args.links:
        client.edit_data_link(instance='simulator', link=link, state='enabled')


def disable(args):
    client = YamcsClient('localhost:8090')
    for link in args.links:
        client.edit_data_link(instance='simulator', link=link, state='disabled')


def configure_list(parser):
    parser.set_defaults(func=list_)


def configure_enable(parser):
    parser.add_argument('links', metavar='<name>', type=str, nargs='+', help='name of the link', default=enable)
    parser.set_defaults(func=enable)


def configure_disable(parser):
    parser.add_argument('links', metavar='<name>', type=str, nargs='+', help='name of the link', default=disable)
    parser.set_defaults(func=disable)


def configure_parser(parser):
    # parser.set_defaults(func=list_)
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List links')
    configure_list(list_parser)

    enable_parser = subparsers.add_parser('enable', help='Enable a link')
    configure_enable(enable_parser)

    disable_parser = subparsers.add_parser('disable', help='Disable a link')
    configure_disable(disable_parser)
