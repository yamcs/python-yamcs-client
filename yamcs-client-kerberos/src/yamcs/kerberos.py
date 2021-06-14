from datetime import datetime, timedelta, timezone

from requests_gssapi import HTTPSPNEGOAuth

from yamcs.core.auth import Credentials
from yamcs.core.exceptions import Unauthorized, YamcsError


class KerberosCredentials(Credentials):
    def __init__(self, access_token=None, expiry=None):
        super().__init__(access_token=access_token, expiry=expiry)

    def login(self, session, auth_url, on_token_update):
        self._on_token_update = on_token_update
        code = self.fetch_authorization_code(session, auth_url)
        creds = self.convert_authorization_code(session, auth_url, code)

        if on_token_update:
            on_token_update(creds)
        return creds

    def refresh(self, session, auth_url):
        code = self.fetch_authorization_code(session, auth_url)
        new_creds = self.convert_authorization_code(session, auth_url, code)

        self.access_token = new_creds.access_token
        self.refresh_token = new_creds.refresh_token
        self.expiry = new_creds.expiry
        if self._on_token_update:
            self._on_token_update(self)

    def fetch_authorization_code(self, session, auth_url):
        auth = HTTPSPNEGOAuth(opportunistic_auth=True)
        response = session.get(auth_url + "/spnego", auth=auth)
        if response.status_code == 401:
            raise Unauthorized("401 Client Error: Unauthorized")
        elif response.status_code == 200:
            return response.text
        else:
            raise YamcsError(f"{response.status_code} Server Error")

    def convert_authorization_code(self, session, auth_url, code):
        data = {"grant_type": "authorization_code", "code": code}
        response = session.post(auth_url + "/token", data=data)
        if response.status_code == 401:
            raise Unauthorized("401 Client Error: Unauthorized")
        elif response.status_code == 200:
            d = response.json()
            expiry = datetime.now(tz=timezone.utc) + timedelta(seconds=d["expires_in"])
            return KerberosCredentials(access_token=d["access_token"], expiry=expiry,)
        else:
            raise YamcsError(f"{response.status_code} Server Error")
