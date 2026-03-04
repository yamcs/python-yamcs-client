import warnings

warnings.warn(
    "The module 'yamcs.core.pagination' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.core.pagination import Iterator  # noqa
