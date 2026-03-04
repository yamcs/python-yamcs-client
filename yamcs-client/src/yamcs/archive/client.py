import warnings

warnings.warn(
    "The module 'yamcs.archive.client' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.archive.client import ArchiveClient  # noqa
