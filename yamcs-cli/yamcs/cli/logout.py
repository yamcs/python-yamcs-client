from __future__ import print_function

from yamcs.cli import utils


class LogoutCommand(utils.Command):

    def __init__(self, parent):
        super(LogoutCommand, self).__init__(parent, 'logout', 'Logout of a Yamcs server')

        self.parser.set_defaults(func=self.do_logout)

    def do_logout(self, args):
        opts = utils.CommandOptions(args)
        if not utils.clear_credentials():
            print('Not logged in to {}'.format(opts.address))
