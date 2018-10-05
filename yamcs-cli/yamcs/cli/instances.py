from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


def list_(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)

    rows = [['NAME', 'STATE', 'MISSION TIME']]
    for instance in client.list_instances():
        rows.append([
            instance.name,
            instance.state,
            instance.mission_time,
        ])
    utils.print_table(rows)


def start(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)

    for instance in args.instances:
        client.start_instance(instance)


def stop(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)

    for instance in args.instances:
        client.stop_instance(instance)


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List instances')
    list_parser.set_defaults(func=list_)

    start_parser = subparsers.add_parser('start', help='Start an instance')
    start_parser.add_argument(
        'instances', metavar='<name>', type=str, nargs='+', help='name of the instance')
    start_parser.set_defaults(func=start)

    stop_parser = subparsers.add_parser('stop', help='Stop an instance')
    stop_parser.add_argument(
        'instances', metavar='<name>', type=str, nargs='+', help='name of the instance')
    stop_parser.set_defaults(func=stop)
