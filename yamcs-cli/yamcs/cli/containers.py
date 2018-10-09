from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


class ContainersCommand(utils.Command):

    def __init__(self, parent):
        super(ContainersCommand, self).__init__(parent, 'containers', 'Read containers')

        subparsers = self.parser.add_subparsers(title='Commands', metavar='COMMAND')

        subparser = self.create_subparser(subparsers, 'list', 'List containers')
        subparser.set_defaults(func=self.list_)

        subparser = self.create_subparser(subparsers, 'describe', 'Describe a container')
        subparser.add_argument('container', metavar='NAME', type=str, help='name of the container')
        subparser.set_defaults(func=self.describe)

    def list_(self, args):
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

    def describe(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)
        mdb = client.get_mdb(opts.instance)
        container = mdb.get_container(args.container)
        print(container._proto)  #pylint: disable=protected-access
