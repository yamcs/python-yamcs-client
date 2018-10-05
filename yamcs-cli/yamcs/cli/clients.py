from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


def list_(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)

    rows = [['ID', 'USER', 'APPLICATION', 'LOGIN']]
    for client in client.list_clients():
        rows.append([
            client.id,
            client.username,
            client.application_name,
            client.login_time,
        ])
    utils.print_table(rows)


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List clients')
    list_parser.set_defaults(func=list_)
