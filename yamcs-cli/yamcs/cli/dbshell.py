from __future__ import print_function

import os
import sys
from cmd import Cmd
from pydoc import pager

import six

from yamcs.cli import utils
from yamcs.client import YamcsClient
from yamcs.core.exceptions import YamcsError

SHOW_OPTIONS = ('databases', 'engines', 'streams', 'tables', 'stream')


class DbShellCommand(utils.Command):

    def __init__(self, parent):
        super(DbShellCommand, self).__init__(parent, 'dbshell', 'Launch Yarch DB Shell', add_epilog=False)

        self.parser.set_defaults(func=self.launch)
        self.parser.add_argument(
            '-c', '--command', metavar='COMMAND', type=str,
            help='SQL command string'
        )

    def launch(self, args):
        opts = utils.CommandOptions(args)
        client = YamcsClient(**opts.client_kwargs)
        shell = DbShell(client)
        shell.do_use(opts.instance)
        if args.command:
            shell.onecmd(args.command)
        else:
            server_info = client.get_server_info()
            intro = (
                'Yamcs DB Shell\n'
                'Server version: {} - ID: {}\n\n'
                'Type ''help'' or ''?'' for help.\n'
            ).format(server_info.version, server_info.id)
            shell.cmdloop(intro)


class DbShell(Cmd):

    pager = False
    prompt = '> '
    instance = None

    tables = []
    streams = []

    def __init__(self, client):
        Cmd.__init__(self)
        self._client = client

    def print_topics(self, header, cmds, cmdlen, maxcol):
        if cmds:
            print('List of dbshell commands:')
            rows = [['?', 'Show help.']]
            for cmd in cmds:
                doc = getattr(self, 'do_' + cmd).__doc__
                if doc:
                    rows.append([cmd, doc])
            utils.print_table(rows)
            print()

    def emptyline(self):
        pass  # Override default behaviour of repeating the last command

    def do_use(self, args):
        """Use another instance, provided as argument."""
        self.instance = args
        self.prompt = self.instance + '> '

        archive = self._client.get_archive(self.instance)
        self.streams = [s.name for s in archive.list_streams()]
        self.tables = [t.name for t in archive.list_tables()]

    def do_pager(self, args):
        """Print results to a pager."""
        self.pager = True

    def do_nopager(self, args):
        """Disable pager. Results are printed to stdout."""
        self.pager = False

    def complete_show(self, text, line, begidx, endidx):
        return [o for o in SHOW_OPTIONS if o.startswith(text)]

    def complete_describe(self, text, line, begidx, endidx):
        return [o for o in (self.streams + self.tables) if o.startswith(text)]

    def default(self, line):
        try:
            for statement in line.split(';'):
                if not statement:
                    continue

                archive = self._client.get_archive(self.instance)
                result = archive.execute_sql(statement)
                if result:
                    self.paginate(result.splitlines() + [''])  # Add an empty line
        except YamcsError as e:
            print(e)

    def do_edit(self, args):
        """Edit a command with $EDITOR."""
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

    def do_exit(self, args):
        """Synonym for quit."""
        return self.do_quit(args)

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
