from __future__ import print_function

from yamcs.cli.utils import print_table
from yamcs.client import YamcsClient


def list_(args):
    client = YamcsClient('localhost:8090')

    rows = [['NAME', 'STATE', 'MISSION TIME']]
    for instance in client.list_instances():
        rows.append([
            instance.name,
            instance.state,
            instance.mission_time,
        ])
    print_table(rows)


def configure_list(parser):
    parser.set_defaults(func=list_)


def configure_parser(parser):
    # parser.set_defaults(func=list_)
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List instances')
    configure_list(list_parser)
