"""
Old-style. For backwards compatibility.
Avoid use.
"""

from yamcs.client.filetransfer.model import (  # noqa
    EntityInfo,
    FileTransferCapabilities,
    FileTransferOption,
    FileTransferService,
    RemoteFile,
    RemoteFileListing,
    Transfer,
)

Service = FileTransferService
"""
Temporary backwards compatibility.
Prefer to use the class 'FileTransferService'.
"""
