import warnings

warnings.warn(
    "The module 'yamcs.storage.model' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.storage.model import Bucket, ObjectInfo, ObjectListing  # noqa
