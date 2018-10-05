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

def _get_address(config):
    return config.get('core', 'host') + ':' + config.get('core', 'port')

def _get_user_agent():
    dist = pkg_resources.get_distribution('yamcs-cli')
    return 'Yamcs CLI v' + dist.version

def create_client(config):
    address = _get_address(config)
    user_agent = _get_user_agent()
    return YamcsClient(address, user_agent=user_agent)


def create_storage_client(config):
    address = _get_address(config)
    user_agent = _get_user_agent()
    return StorageClient(address, user_agent=user_agent)


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
