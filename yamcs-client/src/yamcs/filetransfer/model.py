import threading
from enum import Enum

from yamcs.core.helpers import parse_server_time
from yamcs.protobuf.filetransfer import filetransfer_pb2


class Service:
    def __init__(self, proto, service_client):
        self._proto = proto
        self._service_client = service_client
        self._local_entities = [EntityInfo(entity) for entity in proto.localEntities]
        self._remote_entities = [EntityInfo(entity) for entity in proto.remoteEntities]
        self._capabilities = FileTransferCapabilities(proto.capabilities)
        self._transfer_options = [FileTransferOption(option) for option in
                                  proto.transferOptions]

    @property
    def instance(self):
        """Instance of the service"""
        return self._proto.instance

    @property
    def name(self):
        """Name of this service."""
        return self._proto.name

    @property
    def local_entities(self):
        """List of local entities"""
        return self._local_entities

    @property
    def remote_entities(self):
        """List of remote entities"""
        return self._remote_entities

    @property
    def capabilities(self):
        """Transfer capabilities"""
        return self._capabilities

    @property
    def transfer_options(self):
        """List of possible transfer options"""
        return self._transfer_options

    def upload(
        self,
        bucket_name,
        object_name,
        remote_path,
        source_entity=None,
        destination_entity=None,
        overwrite=True,
        parents=True,
        reliable=False,
        options=None,
    ):
        """
        Uploads a file located in a bucket to a remote destination path.

        .. warning::
            Prefer the use of 'options' instead of the parameters
            overwrite, parents and reliable (deprecated parameters)

        :param str bucket_name: Name of the bucket containing the source object.
        :param str object_name: Name of the source object.
        :param str remote_path: Remote destination.
        :param str source_entity: Use a specific source entity.
                                  (useful in case of multiples)
        :param str destination_entity: Use a specific destination entity.
                                       (useful in case of multiples)
        :param bool overwrite:
            Replace file if it already exists.

            .. deprecated:: 1.8.6
                Use options instead (option name: overwrite)
        :param bool parents:
            Create the remote path if it does not yet exist.

            .. deprecated:: 1.8.6
                Use options instead (option name: createPath)
        :param bool reliable:
            Enable reliable transfers.

            .. deprecated:: 1.8.6
                Use options instead (option name: reliable)
        :param options: file transfer options dict (may overwrite "overwrite", "parents"
                        or "reliable" parameters if set in these options).
        :rtype: .Transfer
        """
        return self._service_client.upload(
            bucket_name=bucket_name,
            object_name=object_name,
            remote_path=remote_path,
            source_entity=source_entity,
            destination_entity=destination_entity,
            overwrite=overwrite,
            parents=parents,
            reliable=reliable,
            options=options,
        )

    def download(
        self,
        bucket_name,
        remote_path,
        object_name=None,
        source_entity=None,
        destination_entity=None,
        overwrite=True,
        parents=True,
        reliable=False,
        options=None,
    ):
        """
        Downloads a file from the source to a bucket.

        .. warning::
            Prefer the use of 'options' instead of the parameters
            overwrite, parents and reliable (deprecated parameters)

        :param str bucket_name: Name of the bucket to receive the file.
        :param str object_name: Name of the file received in the bucket.
        :param str remote_path: Name of the file to be downloaded from the source.
        :param str source_entity: Use a specific source entity.
                                  (useful in case of multiples)
        :param str destination_entity: Use a specific destination entity.
                                       (useful in case of multiples)
        :param bool overwrite:
            Replace file if it already exists.

            .. deprecated:: 1.8.6
                Use options instead (option name: overwrite)
        :param bool parents:
            Create the remote path if it does not yet exist.

            .. deprecated:: 1.8.6
                Use options instead (option name: createPath)
        :param bool reliable:
            Enable reliable transfers.

            .. deprecated:: 1.8.6
                Use options instead (option name: reliable)
        :param options: file transfer options dict (may overwrite "overwrite", "parents"
                        or "reliable" parameters if set in these options).
        :rtype: .Transfer
        """
        return self._service_client.download(
            bucket_name=bucket_name,
            remote_path=remote_path,
            object_name=object_name,
            source_entity=source_entity,
            destination_entity=destination_entity,
            overwrite=overwrite,
            parents=parents,
            reliable=reliable,
            options=options,
        )

    def fetch_filelist(self, remote_path, source_entity=None,
                       destination_entity=None, options=None):
        """
        Sends a request to fetch the directory listing from the remote (destination).

        :param remote_path: path on the remote destination to get the file list
        :param source_entity: source entity requesting the file list
        :param destination_entity: destination entity from which the file list is needed
        :param options: option dictionary
        :return: None
        """
        return self._service_client.fetch_filelist(
            remote_path=remote_path,
            source_entity=source_entity,
            destination_entity=destination_entity,
            options=options,
        )

    def get_filelist(self, remote_path, source_entity=None, destination_entity=None,
                     options=None):
        """
        Returns the latest directory listing for the given destination.

        :param remote_path: path on the remote destination to get the file list
        :param source_entity: source entity requesting the file list
        :param destination_entity: destination entity from which the file list is needed
        :param options: option dictionary
        :return: .RemoteFileListing
        """
        return self._service_client.get_filelist(
            remote_path=remote_path,
            source_entity=source_entity,
            destination_entity=destination_entity,
            options=options,
        )

    def pause_transfer(self, id):
        """
        Pauses a transfer
        """
        self._service_client.pause_transfer(id)

    def resume_transfer(self, id):
        """
        Resume a transfer
        """
        self._service_client.resume_transfer(id)

    def cancel_transfer(self, id):
        """
        Cancel a transfer
        """
        self._service_client.cancel_transfer(id)

    def create_transfer_subscription(self, on_data=None, timeout=60):
        """
        Create a new transfer subscription.

        :param on_data: (Optional) Function that gets called with
                        :class:`.TransferInfo` updates.
        :param timeout: The amount of seconds to wait for the request to
                        complete.
        :type timeout: float
        :return: Future that can be used to manage the background websocket
                 subscription
        :rtype: .TransferSubscription
        """
        return self._service_client.create_transfer_subscription(
            on_data=on_data, timeout=timeout
        )

    def create_filelist_subscription(self, on_data=None, timeout=60):
        """
        Create a new filelist subscription.

        :param on_data: (Optional) Function that gets called with
                        :class:`.TransferInfo` updates.
        :param timeout: The amount of seconds to wait for the request to
                        complete.
        :type timeout: float
        :return: Future that can be used to manage the background websocket
                 subscription
        :rtype: .FileListSubscription
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
    def name(self):
        """Name of the entity"""
        return self._proto.name

    @property
    def id(self):
        """Entity ID"""
        return self._proto.id


class FileTransferCapabilities:
    def __init__(self, proto):
        self._proto = proto

    def __str__(self):
        return str(self._proto)

    @property
    def upload(self):
        return self._proto.upload

    @property
    def download(self):
        return self._proto.download

    @property
    def reliability(self):
        """Deprecated, use FileTransferOption"""
        return self._proto.reliability

    @property
    def remote_path(self):
        return self._proto.remotePath

    @property
    def filelist(self):
        return self._proto.fileList

    @property
    def has_transfer_type(self):
        return self._proto.has_transfer_type


class FileTransferOption:

    class Type(Enum):
        BOOLEAN = 0
        DOUBLE = 1
        STRING = 2

    def __init__(self, proto):
        self._proto = proto
        if proto == filetransfer_pb2.FileTransferOption.Type.BOOLEAN:
            self._type = FileTransferOption.Type.BOOLEAN
        elif proto == filetransfer_pb2.FileTransferOption.Type.DOUBLE:
            self._type = FileTransferOption.Type.DOUBLE
        else:
            self._type = FileTransferOption.Type.STRING
        self._values = [{"value": item.value, "verbose_name": item.verboseName} for
                        item in proto.values]

    @property
    def name(self):
        """Name of the option"""
        return self._proto.name

    @property
    def type(self):
        """Type of the option"""
        return self._type

    @property
    def description(self):
        """Description for the option"""
        return self._proto.description

    @property
    def associated_text(self):
        """Text associated with the option"""
        return self._proto.associatedText

    @property
    def default(self):
        """Default value for the option"""
        return self._proto.default

    @property
    def values(self):
        """List of possible values for the option"""
        return self._values

    @property
    def allow_custom_option(self):
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
    def id(self):
        """Yamcs-local transfer identifier."""
        return self._proto.id

    @property
    def bucket(self):
        return self._proto.bucket

    @property
    def object_name(self):
        return self._proto.objectName

    @property
    def remote_path(self):
        return self._proto.remotePath

    @property
    def time(self):
        """Time when the transfer was started."""
        if self._proto.HasField("startTime"):
            return parse_server_time(self._proto.startTime)
        return None

    @property
    def reliable(self):
        """True if this is a Class 2 CFDP transfer."""
        return self._proto.reliable

    @property
    def state(self):
        """Current transfer state."""
        if self._proto.HasField("state"):
            return filetransfer_pb2.TransferState.Name(self._proto.state)
        return None

    @property
    def size(self):
        """Total bytes to transfer."""
        return self._proto.totalSize

    @property
    def transferred_size(self):
        """Total bytes already transferred."""
        return self._proto.sizeTransferred

    def is_complete(self):
        """
        Returns whether this transfer is complete. A transfer
        can be completed, yet still failed.
        """
        return self.state == "FAILED" or self.state == "COMPLETED"

    def is_success(self):
        """
        Returns true if this transfer was completed successfully.
        """
        return self.state == "COMPLETED"

    @property
    def error(self):
        """Error message in case the transfer failed."""
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

    def await_complete(self, timeout=None):
        """
        Wait for the transfer to be completed.

        :param float timeout: The amount of seconds to wait.
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
    def files(self):
        """List of files"""
        return self._files

    @property
    def destination(self):
        """Remote destination of the file list"""
        return self._proto.destination

    @property
    def remote_path(self):
        """Remote directory of the file list"""
        return self._proto.remotePath

    @property
    def list_time(self):
        """Time the file list was made"""
        return parse_server_time(self._proto.listTime)


class RemoteFile:
    """
    Represents a file on a remote entity.
    """
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Name of the file"""
        return self._proto.name

    @property
    def is_directory(self):
        """Whether the file is a directory"""
        return self._proto.isDirectory

    @property
    def size(self):
        """File size in bytes"""
        return self._proto.size

    @property
    def modified(self):
        """Latest modification time of the file"""
        return parse_server_time(self._proto.modified)
