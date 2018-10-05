from __future__ import print_function

from yamcs.cli import utils


def list_(args):
    config = utils.read_config()
    for section in config.sections():
        print('[{}]'.format(section))
        for k, v in list(config.items(section)):
            print('{} = {}'.format(k, v))


def get(args):
    config = utils.read_config()
    if config.has_option('core', args.property):
        print(config.get('core', args.property))


def set_(args):
    config = utils.read_config()
    if not config.has_section('core'):
        config.add_section('core')
    config.set('core', args.property, args.value)
    utils.save_config(config)


def unset(args):
    config = utils.read_config()
    config.remove_option('core', args.property)
    utils.save_config(config)


def configure_parser(parser):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')

    list_parser = subparsers.add_parser('list', help='List client properties')
    list_parser.set_defaults(func=list_)

    get_parser = subparsers.add_parser('get', help='Get value of client property')
    get_parser.add_argument(
        'property', metavar='<property>', type=str, help='Property')
    get_parser.set_defaults(func=get)

    set_parser = subparsers.add_parser('set', help='Set client property')
    set_parser.add_argument(
        'property', metavar='<property>', type=str, help='Property')
    set_parser.add_argument(
        'value', metavar='<value>', type=str, help='Value')
    set_parser.set_defaults(func=set_)

    unset_parser = subparsers.add_parser('unset', help='Unset client property')
    unset_parser.add_argument(
        'property', metavar='<property>', type=str, help='Property')
    unset_parser.set_defaults(func=unset)
