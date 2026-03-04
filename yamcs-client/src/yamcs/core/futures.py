import warnings

warnings.warn(
    "The module 'yamcs.core.futures' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.core.futures import WebSocketSubscriptionFuture  # noqa
