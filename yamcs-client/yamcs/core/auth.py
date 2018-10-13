from datetime import datetime


class Credentials(object):
    """
    Data holder for different types of credentials. Currently this includes:

    * Username/password credentials (fields ``username`` and ``password``)
    * Bearer tokens (fields ``access_token`` and optionally ``refresh_token``)
    """

    def __init__(self, username=None, password=None, access_token=None,
                 refresh_token=None, expiry=None):
        self.username = username
        """Username (only needed when using username/password credentials)."""

        self.password = password
        """Clear-text password (consider SSL!)."""

        self.access_token = access_token
        """Short-lived bearer token."""

        self.refresh_token = refresh_token
        """Refresh token used to request a new access token (WIP)"""

        self.expiry = expiry
        """When this token expires."""

    def is_expired(self):
        return self.expiry and datetime.utcnow() >= self.expiry
