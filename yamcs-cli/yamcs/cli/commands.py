from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


def list_(args):
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


def describe(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    mdb = client.get_mdb(opts.instance)
    command = mdb.get_command(args.command)
    print(command._proto)  #pylint: disable=protected-access


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List commands')
    list_parser.set_defaults(func=list_)

    describe_parser = subparsers.add_parser('describe', help='Describe a command')
    describe_parser.add_argument(
        'command', metavar='<name>', type=str, help='name of the command')
    describe_parser.set_defaults(func=describe)
