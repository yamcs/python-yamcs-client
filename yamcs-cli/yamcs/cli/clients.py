from __future__ import print_function

from yamcs.cli import utils


def list_(args):
    config = utils.read_config()
    client = utils.create_client(config)

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
    # parser.set_defaults(func=list_)
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List clients')
    list_parser.set_defaults(func=list_)
