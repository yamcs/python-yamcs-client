import warnings

warnings.warn(
    "The module 'yamcs.filetransfer' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.filetransfer.client import FileTransferClient  # noqa
