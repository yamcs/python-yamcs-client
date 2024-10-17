import datetime
import threading
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional

from yamcs.client.core.helpers import parse_server_time
from yamcs.protobuf.filetransfer import filetransfer_pb2

if TYPE_CHECKING:
    from yamcs.client.filetransfer.client import (
        FileListSubscription,
        FileTransferServiceClient,
        TransferSubscription,
    )

__all__ = [
    "EntityInfo",
    "FileTransferCapabilities",
    "FileTransferOption",
    "FileTransferService",
    "RemoteFile",
    "RemoteFileListing",
    "Transfer",
]


class FileTransferService:
    def __init__(self, proto, service_client: "FileTransferServiceClient"):
        self._proto = proto
        self._service_client = service_client
        self._local_entities = [EntityInfo(entity) for entity in proto.localEntities]
        self._remote_entities = [EntityInfo(entity) for entity in proto.remoteEntities]
        self._capabilities = FileTransferCapabilities(proto.capabilities)
        self._transfer_options = [
            FileTransferOption(option) for option in proto.transferOptions
        ]

    @property
    def instance(self) -> str:
        """Instance of the service"""
        return self._proto.instance

    @property
    def name(self) -> str:
        """Name of this service."""
        return self._proto.name

    @property
    def local_entities(self) -> List["EntityInfo"]:
        """List of local entities"""
        return self._local_entities

    @property
    def remote_entities(self) -> List["EntityInfo"]:
        """List of remote entities"""
        return self._remote_entities

    @property
    def capabilities(self) -> "FileTransferCapabilities":
        """Transfer capabilities"""
        return self._capabilities

    @property
    def transfer_options(self) -> List["FileTransferOption"]:
        """List of possible transfer options"""
        return self._transfer_options

    def upload(
        self,
        bucket_name: str,
        object_name: str,
        remote_path: str,
        source_entity: Optional[str] = None,
        destination_entity: Optional[str] = None,
        options: Optional[Mapping[str, Any]] = None,
    ) -> "Transfer":
        """
        Uploads a file located in a bucket to a remote destination path.

        :param bucket_name:
            Name of the bucket containing the source object.
        :param object_name:
            Name of the source object.
        :param remote_path:
            Remote destination.
        :param source_entity:
            Use a specific source entity. (useful in case of multiples)
        :param destination_entity:
            Use a specific destination entity. (useful in case of multiples)
        :param options:
            file transfer options
        """
        return self._service_client.upload(
            bucket_name=bucket_name,
            object_name=object_name,
            remote_path=remote_path,
            source_entity=source_entity,
            destination_entity=destination_entity,
            options=options,
        )

    def download(
        self,
        bucket_name: str,
        remote_path: str,
        object_name: Optional[str] = None,
        source_entity: Optional[str] = None,
        destination_entity: Optional[str] = None,
        options: Optional[Mapping[str, Any]] = None,
    ) -> "Transfer":
        """
        Downloads a file from the source to a bucket.

        :param bucket_name:
            Name of the bucket to receive the file.
        :param object_name:
            Name of the file received in the bucket.
        :param remote_path:
            Name of the file to be downloaded from the source.
        :param source_entity:
            Use a specific source entity. (useful in case of multiples)
        :param destination_entity:
            Use a specific destination entity. (useful in case of multiples)
        :param options:
            File transfer options.
        """
        return self._service_client.download(
            bucket_name=bucket_name,
            remote_path=remote_path,
            object_name=object_name,
            source_entity=source_entity,
            destination_entity=destination_entity,
            options=options,
        )

    def fetch_filelist(
        self,
        remote_path: str,
        source_entity: Optional[str] = None,
        destination_entity: Optional[str] = None,
        options: Optional[Mapping[str, Any]] = None,
    ):
        """
        Sends a request to fetch the directory listing from the remote (destination).

        :param remote_path:
            path on the remote destination to get the file list
        :param source_entity:
            source entity requesting the file list
        :param destination_entity:
            destination entity from which the file list is needed
        :param options:
            option dictionary
        """
        self._service_client.fetch_filelist(
            remote_path=remote_path,
            source_entity=source_entity,
            destination_entity=destination_entity,
            options=options,
        )

    def get_filelist(
        self,
        remote_path: str,
        source_entity: Optional[str] = None,
        destination_entity: Optional[str] = None,
        options: Optional[Mapping[str, Any]] = None,
    ) -> "RemoteFileListing":
        """
        Returns the latest directory listing for the given destination.

        :param remote_path:
            path on the remote destination to get the file list
        :param source_entity:
            source entity requesting the file list
        :param destination_entity:
            destination entity from which the file list is needed
        :param options:
            option dictionary
        """
        return self._service_client.get_filelist(
            remote_path=remote_path,
            source_entity=source_entity,
            destination_entity=destination_entity,
            options=options,
        )

    def pause_transfer(self, id: str) -> None:
        """
        Pauses a transfer
        """
        self._service_client.pause_transfer(id)

    def resume_transfer(self, id: str) -> None:
        """
        Resume a transfer
        """
        self._service_client.resume_transfer(id)

    def cancel_transfer(self, id: str) -> None:
        """
        Cancel a transfer
        """
        self._service_client.cancel_transfer(id)

    def run_file_action(
        self,
        file: str,
        action: str,
        message: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run an action on a remote file.

        Available actions depend on the specific file transfer implementation that
        is in use use.

        .. versionadded:: 1.9.6

        :param file:
            Remote file identifier
        :param action:
            Action identifier
        :param message:
            Action message
        :return:
            Action result (if the action returns anything)
        """
        return self._service_client.run_file_action(file, action, message)

    def create_transfer_subscription(
        self,
        on_data: Optional[Callable[["Transfer"], None]] = None,
        timeout: float = 60,
    ) -> "TransferSubscription":
        """
        Create a new transfer subscription.

        :param on_data:
            Function that gets called with :class:`.Transfer` updates.
        :param timeout:
            The amount of seconds to wait for the request to complete.
        :return:
            Future that can be used to manage the background websocket
            subscription
        :rtype: yamcs.client.filetransfer.client.TransferSubscription
        """
        return self._service_client.create_transfer_subscription(
            on_data=on_data, timeout=timeout
        )

    def create_filelist_subscription(
        self,
        on_data: Optional[Callable[["RemoteFileListing"], None]] = None,
        timeout: float = 60,
    ) -> "FileListSubscription":
        """
        Create a new filelist subscription.

        :param on_data:
            Function that gets called with :class:`.RemoteFileListing` updates.
        :param timeout:
            The amount of seconds to wait for the request to complete.
        :return:
            Future that can be used to manage the background websocket
            subscription
        :rtype: yamcs.client.filetransfer.client.FileListSubscription
        """
        return self._service_client.create_filelist_subscription(
            on_data=on_data, timeout=timeout
        )

    def __str__(self):
        return self.name


class EntityInfo:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Name of the entity"""
        return self._proto.name

    @property
    def id(self) -> str:
        """Entity ID"""
        return self._proto.id


class FileTransferCapabilities:
    def __init__(self, proto):
        self._proto = proto

    @property
    def upload(self) -> bool:
        return self._proto.upload

    @property
    def download(self) -> bool:
        return self._proto.download

    @property
    def remote_path(self) -> bool:
        return self._proto.remotePath

    @property
    def filelist(self) -> bool:
        return self._proto.fileList

    @property
    def has_transfer_type(self) -> bool:
        return self._proto.has_transfer_type

    @property
    def pause_resume(self) -> bool:
        return self._proto.pauseResume

    def __str__(self):
        return str(self._proto)


class FileTransferOption:

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Name of the option"""
        return self._proto.name

    @property
    def type(self) -> str:
        """Type of the option"""
        return filetransfer_pb2.FileTransferOption.Type.Name(self._proto.type)

    @property
    def description(self) -> str:
        """Description for the option"""
        return self._proto.description

    @property
    def associated_text(self) -> str:
        """Text associated with the option"""
        return self._proto.associatedText

    @property
    def default(self) -> Any:
        """Default value for the option"""
        return self._proto.default

    @property
    def values(self):
        """List of possible values for the option"""
        return [
            {"value": item.value, "verbose_name": item.verboseName}
            for item in self._proto.values
        ]

    @property
    def allow_custom_option(self) -> bool:
        """Whether using different values from the pre-set ones is allowed"""
        return self._proto.allowCustomOption

    def __str__(self):
        return str(self._proto)


class Transfer:
    """
    Represents a file transfer.
    """

    def __init__(self, proto, service_client):
        self._proto = proto
        self._service_client = service_client

    @property
    def id(self) -> str:
        """Yamcs-local transfer identifier."""
        return self._proto.id

    @property
    def bucket(self) -> str:
        return self._proto.bucket

    @property
    def object_name(self) -> str:
        return self._proto.objectName

    @property
    def remote_path(self) -> str:
        return self._proto.remotePath

    @property
    def time(self) -> Optional[datetime.datetime]:
        """Time when the transfer was started."""
        if self._proto.HasField("startTime"):
            return parse_server_time(self._proto.startTime)
        return None

    @property
    def reliable(self) -> bool:
        """True if this is a Class 2 CFDP transfer."""
        return self._proto.reliable

    @property
    def state(self) -> Optional[str]:
        """Current transfer state."""
        if self._proto.HasField("state"):
            return filetransfer_pb2.TransferState.Name(self._proto.state)
        return None

    @property
    def size(self) -> int:
        """Total bytes to transfer."""
        return self._proto.totalSize

    @property
    def transferred_size(self) -> int:
        """Total bytes already transferred."""
        return self._proto.sizeTransferred

    def is_complete(self) -> bool:
        """
        Returns whether this transfer is complete. A transfer
        can be completed, yet still failed.
        """
        return self.state == "FAILED" or self.state == "COMPLETED"

    def is_success(self) -> bool:
        """
        Returns true if this transfer was completed successfully.
        """
        return self.state == "COMPLETED"

    @property
    def error(self) -> Optional[str]:
        """
        Error message in case the transfer failed.
        """
        if self.state == "FAILED" and self._proto.HasField("failureReason"):
            return self._proto.failureReason
        return None

    def pause(self):
        """
        Pause this transfer
        """
        self._service_client.pause_transfer(self.id)

    def resume(self):
        """
        Resume this transfer
        """
        self._service_client.resume_transfer(self.id)

    def cancel(self):
        """
        Cancel this transfer
        """
        self._service_client.cancel_transfer(self.id)

    def await_complete(self, timeout: Optional[float] = None):
        """
        Wait for the transfer to be completed.

        :param timeout:
            The amount of seconds to wait.
        """
        completed = threading.Event()

        def callback(updated_transfer):
            if updated_transfer.id == self.id:
                self._proto = updated_transfer._proto
                if self.is_complete():
                    completed.set()

        subscription = self._service_client.create_transfer_subscription(
            on_data=callback
        )

        try:
            if not completed.wait(timeout=timeout):
                # Remark that a timeout does *not* mean that the underlying
                # work is canceled.
                raise TimeoutError("Timed out.")
        finally:
            subscription.cancel()


class RemoteFileListing:
    """
    Represents a list of files from a remote.
    """

    def __init__(self, proto):
        self._proto = proto
        self._files = [RemoteFile(file) for file in proto.files]

    @property
    def files(self) -> List["RemoteFile"]:
        """List of files"""
        return self._files

    @property
    def destination(self) -> str:
        """Remote destination of the file list"""
        return self._proto.destination

    @property
    def remote_path(self) -> str:
        """Remote directory of the file list"""
        return self._proto.remotePath

    @property
    def list_time(self) -> datetime.datetime:
        """Time the file list was made"""
        return parse_server_time(self._proto.listTime)


class RemoteFile:
    """
    Represents a file on a remote entity.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Identifying name of the file"""
        return self._proto.name

    @property
    def display_name(self) -> Optional[str]:
        """
        Optionally, a preferred displayed name of the file.
        """
        if self._proto.HasField("displayName"):
            return self._proto.displayName
        return None

    @property
    def is_directory(self) -> bool:
        """Whether the file is a directory"""
        return self._proto.isDirectory

    @property
    def size(self) -> int:
        """File size in bytes"""
        return self._proto.size

    @property
    def modified(self) -> Optional[datetime.datetime]:
        """Latest modification time of the file"""
        if self._proto.HasField("modified"):
            return parse_server_time(self._proto.modified)
        return None
