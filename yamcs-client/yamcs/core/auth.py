from datetime import datetime


class Credentials(object):
    """
    Data holder for different types of credentials. Currently this includes:

    * Username/password credentials (fields ``username`` and ``password``)
    * Bearer tokens (fields ``access_token`` and optionally ``refresh_token``)
    """

    def __init__(self, username=None, password=None, access_token=None,
                 refresh_token=None, expiry=None, client_id=None,
                 client_secret=None, become=None):
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


    def is_expired(self):
        return self.expiry and datetime.utcnow() >= self.expiry
