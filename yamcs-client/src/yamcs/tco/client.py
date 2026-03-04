import warnings

warnings.warn(
    "The module 'yamcs.tco.client' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.tco.client import TCOClient  # noqa
