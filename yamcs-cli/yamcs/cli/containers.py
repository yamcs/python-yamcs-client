from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


def list_(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    mdb = client.get_mdb(opts.instance)

    rows = [['NAME', 'DESCRIPTION']]
    for container in mdb.list_containers():
        rows.append([
            container.qualified_name,
            container.description,
        ])
    utils.print_table(rows)


def describe(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    mdb = client.get_mdb(opts.instance)
    container = mdb.get_container(args.container)
    print(container._proto)  #pylint: disable=protected-access


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List containers')
    list_parser.set_defaults(func=list_)

    describe_parser = subparsers.add_parser('describe', help='Describe a container')
    describe_parser.add_argument(
        'container', metavar='<name>', type=str, help='name of the container')
    describe_parser.set_defaults(func=describe)
