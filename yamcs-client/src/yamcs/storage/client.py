import warnings

warnings.warn(
    "The module 'yamcs.storage.client' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.storage.client import StorageClient  # noqa
