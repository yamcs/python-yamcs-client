from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


class InstancesCommand(utils.Command):

    def __init__(self, parent):
        super(InstancesCommand, self).__init__(parent, 'instances', 'Read instances')

        subparsers = self.parser.add_subparsers(title='Commands', metavar='COMMAND')

        subparser = self.create_subparser(subparsers, 'list', 'List instances')
        subparser.set_defaults(func=self.list_)

        subparser = self.create_subparser(subparsers, 'start', 'Start an instance')
        subparser.add_argument('instances', metavar='INSTANCE', type=str, nargs='+', help='name of the instance')
        subparser.set_defaults(func=self.start)

        subparser = self.create_subparser(subparsers, 'stop', 'Stop an instance')
        subparser.add_argument('instances', metavar='INSTANCE', type=str, nargs='+', help='name of the instance')
        subparser.set_defaults(func=self.stop)

    def list_(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)

        rows = [['NAME', 'STATE', 'MISSION TIME']]
        for instance in client.list_instances():
            rows.append([
                instance.name,
                instance.state,
                instance.mission_time,
            ])
        utils.print_table(rows)

    def start(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)

        for instance in args.instances:
            client.start_instance(instance)

    def stop(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)

        for instance in args.instances:
            client.stop_instance(instance)
