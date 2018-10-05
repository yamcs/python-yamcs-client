from __future__ import print_function

from yamcs.cli import utils


def list_(args):
    config = utils.read_config()
    client = utils.create_client(config)
    instance = config.get('core', 'instance')

    rows = [['NAME', 'CLASS', 'STATUS']]
    for service in client.list_services(instance):
        rows.append([
            service.name,
            service.class_name,
            service.state,
        ])
    utils.print_table(rows)


def enable(args):
    config = utils.read_config()
    client = utils.create_client(config)
    instance = config.get('core', 'instance')

    for service in args.services:
        client.edit_service(instance, service=service, state='running')


def disable(args):
    config = utils.read_config()
    client = utils.create_client(config)
    instance = config.get('core', 'instance')

    for service in args.services:
        client.edit_service(instance, service=service, state='stopped')


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='Read and manipulate services')
    list_parser.set_defaults(func=list_)

    enable_parser = subparsers.add_parser('enable', help='Enable a service')
    enable_parser.add_argument(
        'services', metavar='<name>', type=str, nargs='+', help='name of the service')
    enable_parser.set_defaults(func=enable)

    disable_parser = subparsers.add_parser('disable', help='Disable a service')
    disable_parser.add_argument(
        'services', metavar='<name>', type=str, nargs='+', help='name of the service')
    disable_parser.set_defaults(func=disable)
