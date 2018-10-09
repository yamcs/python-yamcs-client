from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


class CommandsCommand(utils.Command):

    def __init__(self, parent):
        super(CommandsCommand, self).__init__(parent, 'commands', 'Read commands')

        subparsers = self.parser.add_subparsers(title='Commands', metavar='COMMAND')

        subparser = self.create_subparser(subparsers, 'list', 'List commands')
        subparser.set_defaults(func=self.list_)

        subparser = self.create_subparser(subparsers, 'describe', 'Describe a command')
        subparser.add_argument('command', metavar='NAME', type=str, help='name of the command')
        subparser.set_defaults(func=self.describe)

    def list_(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)
        mdb = client.get_mdb(opts.instance)

        rows = [['NAME', 'DESCRIPTION', 'ABSTRACT']]
        for command in mdb.list_commands():
            rows.append([
                command.qualified_name,
                command.description,
                command.abstract,
            ])
        utils.print_table(rows)

    def describe(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)
        mdb = client.get_mdb(opts.instance)
        command = mdb.get_command(args.command)
        print(command._proto)  #pylint: disable=protected-access
