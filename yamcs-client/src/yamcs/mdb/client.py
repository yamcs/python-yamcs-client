import warnings

warnings.warn(
    "The module 'yamcs.mdb.client' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.mdb.client import MDBClient  # noqa
