from __future__ import print_function

from yamcs.cli.utils import print_table
from yamcs.client import YamcsClient


def list_(args):
    client = YamcsClient('localhost:8090')

    rows = [['NAME', 'TYPE', 'OWNER', 'PERSISTENT', 'MISSION TIME', 'STATE']]
    for processor in client.list_processors(instance='simulator'):
        rows.append([
            processor.name,
            processor.type,
            processor.owner,
            processor.persistent,
            processor.mission_time,
            processor.state,
        ])
    print_table(rows)


def configure_list(parser):
    parser.set_defaults(func=list_)


def configure_parser(parser):
    # parser.set_defaults(func=list_)
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List processors')
    configure_list(list_parser)
