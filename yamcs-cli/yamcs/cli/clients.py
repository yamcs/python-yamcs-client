from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


class ClientsCommand(utils.Command):

    def __init__(self, parent):
        super(ClientsCommand, self).__init__(parent, 'clients', 'Read clients')

        subparsers = self.parser.add_subparsers(title='Commands', metavar='COMMAND')

        subparser = self.create_subparser(subparsers, 'list', 'List clients')
        subparser.set_defaults(func=self.list_)

    def list_(self, args):
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
