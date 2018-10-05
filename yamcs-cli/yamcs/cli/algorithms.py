from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


def list_(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    mdb = client.get_mdb(opts.instance)

    rows = [['NAME', 'DESCRIPTION']]
    for algorithm in mdb.list_algorithms():
        rows.append([
            algorithm.qualified_name,
            algorithm.description,
        ])
    utils.print_table(rows)


def describe(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    mdb = client.get_mdb(opts.instance)
    algorithm = mdb.get_algorithm(args.algorithm)
    print(algorithm._proto)  #pylint: disable=protected-access


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List algorithms')
    list_parser.set_defaults(func=list_)

    describe_parser = subparsers.add_parser('describe', help='Describe an algorithm')
    describe_parser.add_argument(
        'algorithm', metavar='<name>', type=str, help='name of the algorithm')
    describe_parser.set_defaults(func=describe)
