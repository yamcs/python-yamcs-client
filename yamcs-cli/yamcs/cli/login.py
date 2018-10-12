from __future__ import print_function

from getpass import getpass

from yamcs.cli import utils
from yamcs.client import YamcsClient
from yamcs.core import auth


class LoginCommand(utils.Command):

    def __init__(self, parent):
        super(LoginCommand, self).__init__(parent, 'login', 'Login to a Yamcs server')

        self.parser.set_defaults(func=self.do_login)
        self.parser.add_argument('server', metavar='SERVER', type=str, help='name of the server')

    def do_login(self, args):
        client = YamcsClient(args.server)
        auth_info = client.get_auth_info()

        if auth_info.require_authentication:
            username = raw_input('Username: ')
            if not username:
                print('*** Username may not be null')
                return False

            password = getpass('Password: ')
            if not password:
                print('*** Password may not be null')
                return False

            credentials = auth.Credentials(username=username, password=password)
            client = YamcsClient(args.server, credentials=credentials)
            print('Login succeeded')
        else:
            user_info = client.get_user_info()
            print('Anonymous login succeeded (username: {})'.format(user_info.username))

        utils.save_credentials(client.access_token, client.refresh_token)
        server_info = client.get_server_info()

        host, port = client.address.split(':')
        config = utils.read_config()
        if not config.has_section('core'):
            config.add_section('core')
        config.set('core', 'host', host)
        config.set('core', 'port', port)

        if server_info.default_yamcs_instance:
            config.set('core', 'instance', server_info.default_yamcs_instance)
        else:
            config.remove_option('core', 'instance')

        utils.save_config(config)
