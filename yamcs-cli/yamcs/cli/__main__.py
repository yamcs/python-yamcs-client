from __future__ import print_function

import argparse

from yamcs.cli import (algorithms, clients, commands, config, containers,
                       dbshell, instances, links, parameters, processors,
                       services, space_systems, storage, streams, tables,
                       utils)


class SubCommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        # Removes the subparsers metavar from the help output
        parts = super(SubCommandHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = '\n'.join(parts.split('\n')[1:])
        return parts


def main():
    parser = argparse.ArgumentParser(description=None,
                                     formatter_class=SubCommandHelpFormatter)
    parser.add_argument('--version', action='version',
                        version=utils.get_user_agent(),
                        help='Print version information and quit')
    parser.add_argument('--instance', type=str,
                        help='The Yamcs instance to use. Overrides the core/instance property')

    # The width of this impacts the command width of the command column :-/
    metavar = '<command>'

    subparsers = parser.add_subparsers(title='commands', metavar=metavar)

    algorithms_parser = subparsers.add_parser(
        'algorithms', help='Read algorithms')
    algorithms.configure_parser(algorithms_parser)

    clients_parser = subparsers.add_parser('clients', help='List clients')
    clients.configure_parser(clients_parser)

    config_parser = subparsers.add_parser(
        'config', help='Manage Yamcs client properties')
    config.configure_parser(config_parser)

    commands_parser = subparsers.add_parser(
        'commands', help='Read commands')
    commands.configure_parser(commands_parser)

    containers_parser = subparsers.add_parser(
        'containers', help='Read containers')
    containers.configure_parser(containers_parser)

    dbshell_parser = subparsers.add_parser(
        'dbshell', help='Launch Yarch DB Shell')
    dbshell.configure_parser(dbshell_parser)

    instances_parser = subparsers.add_parser(
        'instances', help='Read Yamcs instances')
    instances.configure_parser(instances_parser)

    links_parser = subparsers.add_parser(
        'links', help='Read and manipulate data links')
    links.configure_parser(links_parser)

    parameters_parser = subparsers.add_parser(
        'parameters', help='Read parameters')
    parameters.configure_parser(parameters_parser)

    processors_parser = subparsers.add_parser(
        'processors', help='Read processors')
    processors.configure_parser(processors_parser)

    space_systems_parser = subparsers.add_parser(
        'space-systems', help='Read space systems')
    space_systems.configure_parser(space_systems_parser)

    services_parser = subparsers.add_parser(
        'services', help='Read and manipulate services')
    services.configure_parser(services_parser)

    storage_parser = subparsers.add_parser(
        'storage', help='Manage object storage')
    storage.configure_parser(storage_parser)

    streams_parser = subparsers.add_parser(
        'streams', help='Read and manipulate streams')
    streams.configure_parser(streams_parser)

    tables_parser = subparsers.add_parser(
        'tables', help='Read and manipulate tables')
    tables.configure_parser(tables_parser)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
