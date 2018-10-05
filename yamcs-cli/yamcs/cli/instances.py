from __future__ import print_function

from yamcs.cli import utils


def list_(args):
    config = utils.read_config()
    client = utils.create_client(config)

    rows = [['NAME', 'STATE', 'MISSION TIME']]
    for instance in client.list_instances():
        rows.append([
            instance.name,
            instance.state,
            instance.mission_time,
        ])
    utils.print_table(rows)


def configure_parser(parser):
    # parser.set_defaults(func=list_)
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List instances')
    list_parser.set_defaults(func=list_)
