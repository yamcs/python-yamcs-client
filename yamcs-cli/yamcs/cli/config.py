from __future__ import print_function

from yamcs.cli import utils


class ConfigCommand(utils.Command):

    def __init__(self, parent):
        super(ConfigCommand, self).__init__(parent, 'config', 'Manage Yamcs client properties')

        subparsers = self.parser.add_subparsers(title='Commands', metavar='COMMAND')

        subparser = self.create_subparser(subparsers, 'list', 'List client properties')
        subparser.set_defaults(func=self.list_)

        get_parser = self.create_subparser(subparsers, 'get', 'Get value of client property')
        get_parser.add_argument('property', metavar='PROPERTY', type=str, help='Property')
        get_parser.set_defaults(func=self.get)

        set_parser = self.create_subparser(subparsers, 'set', 'Set client property')
        set_parser.add_argument('property', metavar='PROPERTY', type=str, help='Property')
        set_parser.add_argument('value', metavar='VALUE', type=str, help='Value')
        set_parser.set_defaults(func=self.set_)

        unset_parser = self.create_subparser(subparsers, 'unset', 'Unset client property')
        unset_parser.add_argument('property', metavar='PROPERTY', type=str, help='Property')
        unset_parser.set_defaults(func=self.unset)

    def list_(self, args):
        config = utils.read_config()
        for section in config.sections():
            print('[{}]'.format(section))
            for k, v in list(config.items(section)):
                print('{} = {}'.format(k, v))

    def get(self, args):
        config = utils.read_config()
        if config.has_option('core', args.property):
            print(config.get('core', args.property))

    def set_(self, args):
        config = utils.read_config()
        if not config.has_section('core'):
            config.add_section('core')
        config.set('core', args.property, args.value)
        utils.save_config(config)

    def unset(self, args):
        config = utils.read_config()
        config.remove_option('core', args.property)
        utils.save_config(config)
