import getpass
from datetime import datetime, timedelta

from requests_kerberos import DISABLED, HTTPKerberosAuth
from yamcs.core.auth import Credentials
from yamcs.core.exceptions import Unauthorized, YamcsError


class KerberosCredentials(Credentials):

    principal = None

    def __init__(self, principal=None):
        super().__init__()
        self.principal = principal or getpass.getuser()

    def login(self, session, auth_url, on_token_update):
        self._on_token_update = on_token_update
        code = self.fetch_authorization_code(session, auth_url)
        creds = self.convert_authorization_code(session, auth_url, code)

        if on_token_update:
            on_token_update(creds)
        return creds

    def fetch_authorization_code(self, session, auth_url):
        auth = HTTPKerberosAuth(principal=self.principal,
                                mutual_authentication=DISABLED,
                                force_preemptive=True)
        response = session.get(auth_url + '/spnego', auth=auth)
        if response.status_code == 401:
            raise Unauthorized('401 Client Error: Unauthorized')
        elif response.status_code == 200:
            return response.text
        else:
            raise YamcsError('{} Server Error'.format(response.status_code))

    def convert_authorization_code(self, session, auth_url, code):
        data = {'grant_type': 'authorization_code', 'code': code}
        response = session.post(auth_url + '/token', data=data)
        if response.status_code == 401:
            raise Unauthorized('401 Client Error: Unauthorized')
        elif response.status_code == 200:
            d = response.json()
            expiry = datetime.utcnow() + timedelta(seconds=d['expires_in'])
            return Credentials(access_token=d['access_token'],
                               refresh_token=d['refresh_token'],
                               expiry=expiry)
        else:
            raise YamcsError('{} Server Error'.format(response.status_code))
