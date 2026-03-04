import warnings

warnings.warn(
    "The module 'yamcs.core' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.core import GLOBAL_INSTANCE  # noqa
