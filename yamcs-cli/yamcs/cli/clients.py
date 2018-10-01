from __future__ import print_function

from yamcs.cli.utils import print_table
from yamcs.client import YamcsClient


def list_(args):
    client = YamcsClient('localhost:8090')

    rows = [['ID', 'USER', 'APPLICATION', 'LOGIN']]
    for client in client.list_clients(instance='simulator'):
        rows.append([
            client.id,
            client.username,
            client.application_name,
            client.login_time,
        ])
    print_table(rows)


def configure_list(parser):
    parser.set_defaults(func=list_)


def configure_parser(parser):
    # parser.set_defaults(func=list_)
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List clients')
    configure_list(list_parser)
