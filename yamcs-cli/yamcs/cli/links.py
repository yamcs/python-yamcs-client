from __future__ import print_function

from yamcs.cli import utils


def list_(args):
    config = utils.read_config()
    client = utils.create_client(config)
    instance = config.get('core', 'instance')

    rows = [['NAME', 'CLASS', 'STATUS', 'IN', 'OUT']]
    for link in client.list_data_links(instance):
        rows.append([
            link.name,
            link.class_name,
            link.status,
            link.in_count,
            link.out_count,
        ])
    utils.print_table(rows)


def enable(args):
    config = utils.read_config()
    client = utils.create_client(config)
    instance = config.get('core', 'instance')

    for link in args.links:
        client.edit_data_link(instance, link=link, state='enabled')


def disable(args):
    config = utils.read_config()
    client = utils.create_client(config)
    instance = config.get('core', 'instance')

    for link in args.links:
        client.edit_data_link(instance, link=link, state='disabled')


def configure_parser(parser):
    # parser.set_defaults(func=list_)
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
