import warnings

warnings.warn(
    "The module 'yamcs.core.exceptions' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.core.exceptions import (  # noqa
    ConnectionFailure,
    NotFound,
    TimeoutError,
    Unauthorized,
    YamcsError,
)
