from __future__ import print_function

from getpass import getpass

from six.moves import input

from yamcs.cli import utils
from yamcs.client import YamcsClient
from yamcs.core import auth


class LoginCommand(utils.Command):

    def __init__(self, parent):
        super(LoginCommand, self).__init__(parent, 'login', 'Login to a Yamcs server')

        self.parser.set_defaults(func=self.do_login)
        self.parser.add_argument('address', metavar='HOST[:PORT]', nargs='?', type=str, help='server address (example: localhost:8090)')

    def do_login(self, args):
        opts = utils.CommandOptions(args)

        address = args.address or self.read_address(opts)
        client = YamcsClient(address)
        auth_info = client.get_auth_info()

        if auth_info.require_authentication:
            credentials = self.read_credentials()
            client = YamcsClient(address, credentials=credentials)
            print('Login succeeded')
        else:
            user_info = client.get_user_info()
            print('Anonymous login succeeded (username: {})'.format(user_info.username))

        self.save_client_config(client, opts.config)

    def read_address(self, opts):
        default_host = opts.host or 'localhost'
        default_port = opts.port or 8090
        host = input('Host [{}]: '.format(default_host)) or default_host
        port = input('Port [{}]: '.format(default_port)) or default_port
        return '{}:{}'.format(host, port)

    def read_credentials(self):
        username = input('Username: ')
        if not username:
            print('*** Username may not be null')
            return False

        password = getpass('Password: ')
        if not password:
            print('*** Password may not be null')
            return False

        return auth.Credentials(username=username, password=password)

    def save_client_config(self, client, config):
        utils.save_credentials(client.credentials)
        server_info = client.get_server_info()

        host, port = client.address.split(':')
        if not config.has_section('core'):
            config.add_section('core')
        config.set('core', 'host', host)
        config.set('core', 'port', port)

        if server_info.default_yamcs_instance:
            config.set('core', 'instance', server_info.default_yamcs_instance)
        else:
            config.remove_option('core', 'instance')
        utils.save_config(config)
