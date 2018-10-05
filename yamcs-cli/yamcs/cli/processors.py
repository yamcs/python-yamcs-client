from __future__ import print_function

from yamcs.cli import utils


def list_(args):
    config = utils.read_config()
    client = utils.create_client(config)
    instance = config.get('core', 'instance')

    rows = [['NAME', 'TYPE', 'OWNER', 'PERSISTENT', 'MISSION TIME', 'STATE']]
    for processor in client.list_processors(instance):
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
    # parser.set_defaults(func=list_)
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List processors')
    list_parser.set_defaults(func=list_)
