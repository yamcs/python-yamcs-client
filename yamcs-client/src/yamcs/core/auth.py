import warnings

warnings.warn(
    "The module 'yamcs.core.auth' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.core.auth import (  # noqa
    APIKeyCredentials,
    BasicAuthCredentials,
    Credentials,
)
