import warnings

warnings.warn(
    "The module 'yamcs.filetransfer.model' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

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
