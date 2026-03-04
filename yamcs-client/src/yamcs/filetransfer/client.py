import warnings

warnings.warn(
    "The module 'yamcs.filetransfer.client' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.filetransfer.model import (  # noqa
    FileListSubscription,
    FileTransferClient,
    FileTransferServiceClient,
    TransferSubscription,
)

ServiceClient = FileTransferServiceClient
"""
Temporary backwards compatibility.
Prefer to use the class 'FileTransferServiceService'.
"""
