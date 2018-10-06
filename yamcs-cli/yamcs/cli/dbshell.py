from __future__ import print_function

import os
import sys
from cmd import Cmd
from pydoc import pager

import six

from yamcs.cli import utils
from yamcs.client import YamcsClient
from yamcs.core.exceptions import YamcsError

SHOW_OPTIONS = ('streams', 'tables')


class DbShell(Cmd):

    ruler = '-'
    doc_header = 'Available commands (type help <command>)'
    pager = True

    def __init__(self, archive):
        Cmd.__init__(self)
        self._archive = archive

    def emptyline(self):
        pass  # Override default behaviour of repeating the last command

    def do_pager(self, args):
        """Print result via a pager."""
        self.pager = True

    def do_nopager(self, args):
        """Disable pager. Results are printed to stdout."""
        self.pager = False

    def complete_show(self, text, line, begidx, endidx):
        return [o for o in SHOW_OPTIONS if o.startswith(text)]

    def default(self, line):
        try:
            result = self._archive.execute_sql(line)
            if result:
                self.paginate(result.splitlines())
        except YamcsError as e:
            print(e)

    def do_edit(self, args):
        if 'EDITOR' not in os.environ:
            print('*** $EDITOR not set')
        else:
            path = os.path.join(utils.CONFIG_DIR, 'sql')
            cmd = os.environ['EDITOR']
            try:
                os.system(cmd + ' ' + path)
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        sql = f.read()
                        if sql:
                            self.default(sql)
            finally:
                if os.path.exists(path):
                    os.remove(path)

    def do_quit(self, args):
        """Quits the DB Shell."""
        return True

    def do_system(self, args):
        """Execute a system command."""
        os.system(args)

    def paginate(self, lines):
        if self.pager:
            output = six.StringIO()
        else:
            output = sys.stdout

        for line in lines:
            print(line, file=output)

        if self.pager:
            output.seek(0)
            pager(output.read())


def launch(args):
    opts = utils.CommandOptions(args)
    client = YamcsClient(**opts.client_kwargs)
    archive = client.get_archive(opts.instance)
    shell = DbShell(archive)

    shell.prompt = opts.instance + '> '
    try:
        if args.command:
            shell.pager = False
            shell.onecmd(args.command)
        elif args.no_intro:
            shell.cmdloop()
        else:
            # shell.onecmd('help')
            shell.cmdloop('Yamcs DB Shell\n\n'
                          'Type: edit                    Edit a command with $EDITOR\n'
                          '      nopager                 Disable pager\n'
                          '      pager                   Enable pager\n'
                          '      system <command>        Execute a system command\n'
                          '      help                    Show help\n')
    except KeyboardInterrupt:
        print()  # Move user below current prompt


def configure_parser(parser):
    parser.set_defaults(func=launch)
    parser.add_argument(
        '-c', '--command', metavar='<command>', type=str, help='SQL command string'
    )
    parser.add_argument(
        '--no-intro', action='store_true', help='Hide the intro message'
    )
