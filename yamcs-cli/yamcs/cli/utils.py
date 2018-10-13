from __future__ import print_function

import argparse
import json
import os

import pkg_resources

from yamcs.core import auth
from yamcs.core.helpers import parse_isostring, to_isostring

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser

HOME = os.path.expanduser('~')
CONFIG_DIR = os.path.join(os.path.join(HOME, '.config'), 'yamcs-cli')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config')
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'credentials')

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


def save_credentials(credentials):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    with open(CREDENTIALS_FILE, 'wb') as f:
        json.dump({
            'access_token': credentials.access_token,
            'refresh_token': credentials.refresh_token,
            'expiry': to_isostring(credentials.expiry),
        }, f, indent=2)


def read_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'rb') as f:
            d = json.load(f)
            access_token = d['access_token']
            refresh_token = d['refresh_token']
            expiry = parse_isostring(d['expiry']) if 'expiry' in d else None
            return auth.Credentials(
                access_token=access_token,
                refresh_token=refresh_token,
                expiry=expiry,
            )
    return None


def clear_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        os.remove(CREDENTIALS_FILE)
        return True
    return False


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
        subparser = subparsers.add_parser(command, help=help_, add_help=False,
                                          formatter_class=SubCommandHelpFormatter,
                                          epilog=epilog)
        # the usage string of every command
        subparser.add_argument('-h', '--help', action='help',
                               default=argparse.SUPPRESS, help=argparse.SUPPRESS)
        return subparser


class CommandOptions(object):

    def __init__(self, args):
        self.config = read_config()
        self._credentials = read_credentials()
        self._args = args

    @property
    def instance(self):
        return self._args.instance or self.config.get('core', 'instance')

    @property
    def host(self):
        return self.config.get('core', 'host')

    @property
    def port(self):
        return self.config.get('core', 'port')

    @property
    def address(self):
        return self.host + ':' + self.port

    @property
    def user_agent(self):
        return get_user_agent()

    def _on_token_update(self, credentials):
        print('updating creds..', credentials)
        save_credentials(credentials)

    @property
    def client_kwargs(self):
        return {
            'address': self.address,
            'user_agent': self.user_agent,
            'credentials': self._credentials,
            'on_token_update': self._on_token_update,
        }


class SubCommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        # Removes the subparsers metavar from the help output
        parts = super(SubCommandHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = '\n'.join(parts.split('\n')[1:])
        return parts
