from __future__ import print_function

from yamcs.cli import utils


def list_(args):
    config = utils.read_config()
    client = utils.create_client(config)
    instance = args.instance or config.get('core', 'instance')

    rows = [['NAME', 'CLASS', 'STATUS']]
    for service in client.list_services(instance):
        rows.append([
            service.name,
            service.class_name,
            service.state,
        ])
    utils.print_table(rows)


def start(args):
    config = utils.read_config()
    client = utils.create_client(config)
    instance = args.instance or config.get('core', 'instance')

    for service in args.services:
        client.edit_service(instance, service=service, state='running')


def stop(args):
    config = utils.read_config()
    client = utils.create_client(config)
    instance = args.instance or config.get('core', 'instance')

    for service in args.services:
        client.edit_service(instance, service=service, state='stopped')


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='Read and manipulate services')
    list_parser.set_defaults(func=list_)

    start_parser = subparsers.add_parser('start', help='Start a service')
    start_parser.add_argument(
        'services', metavar='<name>', type=str, nargs='+', help='name of the service')
    start_parser.set_defaults(func=start)

    stop_parser = subparsers.add_parser('stop', help='Stop a service')
    stop_parser.add_argument(
        'services', metavar='<name>', type=str, nargs='+', help='name of the service')
    stop_parser.set_defaults(func=stop)
