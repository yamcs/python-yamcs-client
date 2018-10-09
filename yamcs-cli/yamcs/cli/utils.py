from __future__ import print_function

import argparse
import os

import pkg_resources

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser

HOME = os.path.expanduser('~')
CONFIG_DIR = os.path.join(os.path.join(HOME, '.config'), 'yamcs-cli')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config')

def get_user_agent():
    dist = pkg_resources.get_distribution('yamcs-cli')
    return 'Yamcs CLI v' + dist.version


def read_config():
    config = ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)

    return config


def save_config(config):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    with open(CONFIG_FILE, 'wb') as f:
        config.write(f)


def print_table(rows, decorate=False, header=False):
    widths = map(len, rows[0])
    for row in rows:
        for idx, col in enumerate(row):
            widths[idx] = max(len(str(col)), widths[idx])

    separator = '  '
    prefix = '| ' if decorate else ''
    suffix = ' |' if decorate else ''

    total_width = len(prefix) + len(suffix)
    for width in widths:
        total_width += width
    total_width += len(separator) * (len(widths) - 1)

    data = rows[1:] if header else rows
    if header and data:
        if decorate:
            print('+{}+'.format('-' * (total_width - 2)))
        cols = separator.join([
            str.ljust(str(col), width)
            for col, width in zip(rows[0], widths)])
        print(prefix + cols + suffix)
    if data:
        if decorate:
            print('+{}+'.format('-' * (total_width - 2)))
        for row in data:
            cols = separator.join([
                str.ljust(str(col), width)
                for col, width in zip(row, widths)])
            print(prefix + cols + suffix)
        if decorate:
            print('+{}+'.format('-' * (total_width - 2)))


class Command(object):

    def __init__(self, subparsers, command, help_, add_epilog=True):
        self.parser = self.create_subparser(subparsers, command, help_, add_epilog=add_epilog)

    def create_subparser(self, subparsers, command, help_, add_epilog=True):
        epilog = None
        if add_epilog:
            epilog = 'Run \'yamcs {} COMMAND --help\' for more information on a command.'.format(command)

        # Override the default help action so that it does not show up in
        # the usage string of every command
        subparser = subparsers.add_parser(command, help=help_, add_help=False,
                                          formatter_class=SubCommandHelpFormatter,
                                          epilog=epilog)
        subparser.add_argument('-h', '--help', action='help',
                               default=argparse.SUPPRESS, help=argparse.SUPPRESS)
        return subparser


class CommandOptions(object):

    def __init__(self, args):
        self._config = read_config()
        self._args = args

    @property
    def instance(self):
        return self._args.instance or self._config.get('core', 'instance')

    @property
    def address(self):
        return self._config.get('core', 'host') + ':' + self._config.get('core', 'port')

    @property
    def user_agent(self):
        return get_user_agent()

    @property
    def client_kwargs(self):
        return {
            'address': self.address,
            'user_agent': self.user_agent,
        }


class SubCommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        # Removes the subparsers metavar from the help output
        parts = super(SubCommandHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = '\n'.join(parts.split('\n')[1:])
        return parts
