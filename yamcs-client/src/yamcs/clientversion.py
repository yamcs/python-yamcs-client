import warnings

warnings.warn(
    "The module 'yamcs.clientversion' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.clientversion import __version__  # noqa
