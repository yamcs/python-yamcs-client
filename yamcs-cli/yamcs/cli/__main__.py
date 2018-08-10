from __future__ import print_function

import argparse

from yamcs.cli import links


class SubCommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        # Removes the subparsers metavar from the help output
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = '\n'.join(parts.split('\n')[1:])
        return parts





def services(args):
    print('services')


def main():
    parser = argparse.ArgumentParser(description=None,
                                     formatter_class=SubCommandHelpFormatter)
    parser.add_argument('--version', action='version', version='yamcs-cli vTODO',
                        help='Print version information and quit')
    
    metavar='<command>'  # The width of this impacts the command width of the command column :-/
    subparsers = parser.add_subparsers(title='commands', metavar=metavar)

    clients_parser = subparsers.add_parser('clients', help='List clients')

    config_parser = subparsers.add_parser('config',
                                          help='Manage Yamcs client properties')

    instances_parser = subparsers.add_parser('instances',
                                             help='Read Yamcs instances')

    links_parser = subparsers.add_parser('links',
                                         help='Read and manipulate data links')
    links.configure_parser(links_parser)
    
    services_parser = subparsers.add_parser('services', 
                                            help='Read and manipulate services')
    services_parser.set_defaults(func=services)

    storage_parser = subparsers.add_parser('storage',
                                           help='Manage object storage')

    tables_parser = subparsers.add_parser('tables',
                                          help='Read and manipulate tables')

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
