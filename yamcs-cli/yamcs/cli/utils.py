from __future__ import print_function

import os

import pkg_resources

from yamcs.client import YamcsClient
from yamcs.storage import Client as StorageClient

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


def print_table(rows):
    widths = map(len, rows[0])
    for row in rows:
        for idx, col in enumerate(row):
            widths[idx] = max(len(str(col)), widths[idx])

    for row in rows:
        print('  '.join([
            str.ljust(str(col), width)
            for col, width in zip(row, widths)]))


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
