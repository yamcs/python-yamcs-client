from datetime import datetime, timedelta, timezone

from requests.auth import HTTPBasicAuth
from yamcs.core.exceptions import Unauthorized, YamcsError


def _convert_user_credentials(
    session, token_url, username=None, password=None, refresh_token=None
):
    """
    Converts username/password credentials to token credentials by
    using Yamcs as the authentication server.
    """
    if username and password:
        data = {"grant_type": "password", "username": username, "password": password}
    elif refresh_token:
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    else:
        raise NotImplementedError()

    response = session.post(token_url, data=data)
    if response.status_code == 401:
        raise Unauthorized("401 Client Error: Unauthorized")
    elif response.status_code == 200:
        d = response.json()
        expiry = datetime.now(tz=timezone.utc) + timedelta(seconds=d["expires_in"])
        return Credentials(
            access_token=d["access_token"],
            refresh_token=d["refresh_token"],
            expiry=expiry,
        )
    else:
        raise YamcsError(f"{response.status_code} Server Error")


def _convert_service_account_credentials(
    session, token_url, client_id, client_secret, become
):
    """
    Converts service account credentials to impersonated token credentials.
    """
    data = {"grant_type": "client_credentials", "become": become}

    response = session.post(
        token_url, data=data, auth=HTTPBasicAuth(client_id, client_secret)
    )
    if response.status_code == 401:
        raise Unauthorized("401 Client Error: Unauthorized")
    elif response.status_code == 200:
        d = response.json()
        expiry = datetime.now(tz=timezone.utc) + timedelta(seconds=d["expires_in"])
        return Credentials(
            access_token=d["access_token"],
            client_id=client_id,
            client_secret=client_secret,
            become=become,
            expiry=expiry,
        )
    else:
        raise YamcsError(f"{response.status_code} Server Error")


class Credentials:
    """
    Data holder for different types of credentials. Currently this includes:

    * Username/password credentials (fields ``username`` and ``password``)
    * Bearer tokens (fields ``access_token`` and optionally ``refresh_token``)
    """

    def __init__(
        self,
        username=None,
        password=None,
        access_token=None,
        refresh_token=None,
        expiry=None,
        client_id=None,
        client_secret=None,
        become=None,
    ):
        self.username = username
        """Username (only needed when using username/password credentials)."""

        self.password = password
        """Clear-text password (consider TLS!)."""

        self.access_token = access_token
        """Short-lived bearer token."""

        self.refresh_token = refresh_token
        """Refresh token used to request a new access token."""

        self.expiry = expiry
        """When this token expires."""

        self.client_id = client_id
        """The client ID. Currently used only by service accounts."""

        self.client_secret = client_secret
        """The client secret. Currently used only by service accounts."""

        self.become = become
        """
        Name of the user to impersonate. Only service accounts with
        impersonation authority can use this feature.
        """

        self._on_token_update = None

    def login(self, session, auth_url, on_token_update):
        self._on_token_update = on_token_update
        token_url = auth_url + "/token"
        if self.username:  # Convert u/p to bearer
            creds = _convert_user_credentials(
                session, token_url, username=self.username, password=self.password
            )
        elif self.become:  # Impersonate from service account
            creds = _convert_service_account_credentials(
                session,
                token_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
                become=self.become,
            )
        else:
            creds = self

        if on_token_update:
            on_token_update(creds)
        return creds

    def is_expired(self):
        return self.expiry and datetime.now(tz=timezone.utc) >= self.expiry

    def refresh(self, session, auth_url):
        if self.become:
            new_creds = _convert_service_account_credentials(
                session,
                auth_url + "/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                become=self.become,
            )
        elif self.refresh_token:
            new_creds = _convert_user_credentials(
                session, auth_url + "/token", refresh_token=self.refresh_token
            )
        else:
            raise YamcsError("Missing refresh token")

        self.access_token = new_creds.access_token
        self.refresh_token = new_creds.refresh_token
        self.expiry = new_creds.expiry
        if self._on_token_update:
            self._on_token_update(self)

    def before_request(self, session, auth_url):
        if self.is_expired():
            self.refresh(session, auth_url)

        if self.access_token:
            session.headers.update({"Authorization": "Bearer " + self.access_token})
