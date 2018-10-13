from __future__ import print_function

import argparse

from yamcs.cli import utils
from yamcs.cli.algorithms import AlgorithmsCommand
from yamcs.cli.clients import ClientsCommand
from yamcs.cli.commands import CommandsCommand
from yamcs.cli.config import ConfigCommand
from yamcs.cli.containers import ContainersCommand
from yamcs.cli.dbshell import DbShellCommand
from yamcs.cli.instances import InstancesCommand
from yamcs.cli.links import LinksCommand
from yamcs.cli.login import LoginCommand
from yamcs.cli.logout import LogoutCommand
from yamcs.cli.parameters import ParametersCommand
from yamcs.cli.processors import ProcessorsCommand
from yamcs.cli.services import ServicesCommand
from yamcs.cli.space_systems import SpaceSystemsCommand
from yamcs.cli.storage import StorageCommand
from yamcs.cli.streams import StreamsCommand
from yamcs.cli.tables import TablesCommand
from yamcs.core.exceptions import Unauthorized


def create_subparser(subparsers, command, help_):
    # Override the default help action so that it does not show up in
    # the usage string of every command
    subparser = subparsers.add_parser(command, help=help_, add_help=False)
    subparser.add_argument('-h', '--help', action='help',
                           default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    return subparser


def main():
    parser = argparse.ArgumentParser(description=None, formatter_class=utils.SubCommandHelpFormatter,
                                     epilog='Run \'yamcs COMMAND --help\' for more information on a command.')
    parser.add_argument('--version', action='version',
                        version=utils.get_user_agent(),
                        help='Print version information and quit')
    parser.add_argument('--instance', type=str,
                        help='The Yamcs instance to use. Overrides the core/instance property')

    # The width of this impacts the command width of the command column :-/
    metavar = 'COMMAND'

    subparsers = parser.add_subparsers(title='Commands', metavar=metavar)

    AlgorithmsCommand(subparsers)
    ClientsCommand(subparsers)
    CommandsCommand(subparsers)
    ConfigCommand(subparsers)
    ContainersCommand(subparsers)
    DbShellCommand(subparsers)
    InstancesCommand(subparsers)
    LinksCommand(subparsers)
    LoginCommand(subparsers)
    LogoutCommand(subparsers)
    ParametersCommand(subparsers)
    ProcessorsCommand(subparsers)
    SpaceSystemsCommand(subparsers)
    ServicesCommand(subparsers)
    StorageCommand(subparsers)
    StreamsCommand(subparsers)
    TablesCommand(subparsers)

    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print()  # Clear prompt
    except Unauthorized:
        print('Unauthorized. Run: \'yamcs login\' to login to Yamcs')
    except Exception as e:  # pylint: disable=W0703
        print(e)


if __name__ == '__main__':
    main()
