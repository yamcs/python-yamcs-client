"""
Old-style. For backwards compatibility.
Avoid use.
"""

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
