from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


def list_(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    mdb = client.get_mdb(opts.instance)

    rows = [['NAME', 'DESCRIPTION']]
    for space_system in mdb.list_space_systems():
        rows.append([
            space_system.qualified_name,
            space_system.description,
        ])
    utils.print_table(rows)


def describe(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    mdb = client.get_mdb(opts.instance)
    space_system = mdb.get_space_system(args.space_system)
    print(space_system._proto)  #pylint: disable=protected-access


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List space systems')
    list_parser.set_defaults(func=list_)

    describe_parser = subparsers.add_parser('describe', help='Describe a space system')
    describe_parser.add_argument(
        'space_system', metavar='<name>', type=str, help='name of the space system')
    describe_parser.set_defaults(func=describe)
