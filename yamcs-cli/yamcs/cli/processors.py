from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


def list_(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)

    rows = [['NAME', 'TYPE', 'OWNER', 'PERSISTENT', 'MISSION TIME', 'STATE']]
    for processor in client.list_processors(opts.instance):
        rows.append([
            processor.name,
            processor.type,
            processor.owner,
            processor.persistent,
            processor.mission_time,
            processor.state,
        ])
    utils.print_table(rows)


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List processors')
    list_parser.set_defaults(func=list_)
