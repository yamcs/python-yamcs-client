from __future__ import print_function

from yamcs.cli import utils
from yamcs.client import YamcsClient


class ProcessorsCommand(utils.Command):

    def __init__(self, parent):
        super(ProcessorsCommand, self).__init__(parent, 'processors', 'Read processors')

        subparsers = self.parser.add_subparsers(title='Commands', metavar='COMMAND')

        subparser = self.create_subparser(subparsers, 'list', 'List processors')
        subparser.set_defaults(func=self.list_)

    def list_(self, args):
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
