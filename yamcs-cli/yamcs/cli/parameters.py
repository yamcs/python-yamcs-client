from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


def list_(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    mdb = client.get_mdb(opts.instance)

    rows = [['NAME', 'DATA SOURCE']]
    for parameter in mdb.list_parameters():
        rows.append([
            parameter.qualified_name,
            parameter.data_source,
        ])
    utils.print_table(rows)


def describe(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    mdb = client.get_mdb(opts.instance)
    parameter = mdb.get_parameter(args.parameter)
    print(parameter._proto)  #pylint: disable=protected-access


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List parameters')
    list_parser.set_defaults(func=list_)

    describe_parser = subparsers.add_parser('describe', help='Describe a parameter')
    describe_parser.add_argument(
        'parameter', metavar='<name>', type=str, help='name of the parameter')
    describe_parser.set_defaults(func=describe)
