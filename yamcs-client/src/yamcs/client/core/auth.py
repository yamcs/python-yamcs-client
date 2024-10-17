import base64
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

import requests
from requests.auth import HTTPBasicAuth
from yamcs.client.core.exceptions import Unauthorized, YamcsError
from yamcs.client.core.helpers import do_post

__all__ = [
    "APIKeyCredentials",
    "BasicAuthCredentials",
    "Credentials",
]


def _convert_user_credentials(
    session: requests.Session,
    token_url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> "Credentials":
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

    response = do_post(session, token_url, data=data)
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
    session: requests.Session,
    token_url: str,
    client_id: str,
    client_secret: str,
    become: str,
) -> "Credentials":
    """
    Converts service account credentials to impersonated token credentials.
    """
    data = {"grant_type": "client_credentials", "become": become}

    response = do_post(
        session,
        token_url,
        data=data,
        auth=HTTPBasicAuth(client_id, client_secret),
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
        username: Optional[str] = None,
        password: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        expiry: Optional[datetime] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        become: Optional[str] = None,
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

    def login(
        self,
        session: requests.Session,
        auth_url: str,
        on_token_update: Optional[Callable[["Credentials"], None]],
    ) -> "Credentials":
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
                client_id=str(self.client_id),
                client_secret=str(self.client_secret),
                become=self.become,
            )
        else:
            creds = self

        if on_token_update:
            on_token_update(creds)
        return creds

    def is_expired(self) -> bool:
        if self.expiry is not None:
            return self.expiry and datetime.now(tz=timezone.utc) >= self.expiry
        else:
            return False

    def refresh(self, session: requests.Session, auth_url: str):
        if self.become:
            new_creds = _convert_service_account_credentials(
                session,
                auth_url + "/token",
                client_id=str(self.client_id),
                client_secret=str(self.client_secret),
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

    def before_request(self, session: requests.Session, auth_url: str):
        if self.is_expired():
            self.refresh(session, auth_url)

        if self.access_token:
            session.headers.update({"Authorization": "Bearer " + self.access_token})


class BasicAuthCredentials(Credentials):
    """
    Data holder for Basic Auth credentials. This includes a username and a password
    which are passed in the HTTP Authorization header on each request.
    """

    def __init__(self, username: str, password: str):
        super().__init__(username=username, password=password)

    def is_expired(self) -> bool:
        return False

    def refresh(self):
        pass

    def login(self, *args, **kwargs):
        return self

    def before_request(self, session: requests.Session, auth_url: str):
        buf = str.encode(f"{self.username}:{self.password}")
        usernamePass = base64.b64encode(buf).decode()
        session.headers.update({"Authorization": "Basic " + usernamePass})


class APIKeyCredentials(Credentials):
    def __init__(self, key: str):
        super().__init__(password=key)

    def is_expired(self) -> bool:
        return False

    def refresh(self):
        pass

    def login(self, *args, **kwargs):
        return self

    def before_request(self, session: requests.Session, auth_url: str):
        session.headers.update({"x-api-key": str(self.password)})
