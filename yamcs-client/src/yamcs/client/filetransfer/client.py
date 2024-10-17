import functools
import json
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional

from google.protobuf import json_format, struct_pb2
from yamcs.client.core.context import Context
from yamcs.client.core.exceptions import NotFound
from yamcs.client.core.futures import WebSocketSubscriptionFuture
from yamcs.client.core.subscriptions import WebSocketSubscriptionManager
from yamcs.client.filetransfer.model import (
    FileTransferService,
    RemoteFileListing,
    Transfer,
)
from yamcs.protobuf.filetransfer import filetransfer_pb2

__all__ = [
    "FileListSubscription",
    "FileTransferClient",
    "FileTransferServiceClient",
    "TransferSubscription",
]


def _wrap_callback_parse_transfer_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse TransferInfo
    from a WebSocket data message
    """
    pb = filetransfer_pb2.TransferInfo()
    message.Unpack(pb)
    transfer = subscription._process(pb)
    if on_data:
        on_data(transfer)


def _wrap_callback_parse_filelist_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse ListFilesResponse
    from a WebSocket data message
    """
    pb = filetransfer_pb2.ListFilesResponse()
    message.Unpack(pb)
    filelist = subscription._process(pb)
    if on_data:
        on_data(filelist)


class TransferSubscription(WebSocketSubscriptionFuture):
    """
    Local object providing access to transfer updates.

    A subscription object stores the last transfer info for
    each transfer.
    """

    def __init__(self, manager, service_client: "FileTransferServiceClient"):
        super(TransferSubscription, self).__init__(manager)
        self.service_client = service_client
        self._cache = {}
        """Transfer cache keyed by id."""

    def get_transfer(self, id: str) -> Optional[Transfer]:
        """
        Returns the latest transfer state.

        :param id:
            Transfer identifier
        """
        if id in self._cache:
            return self._cache[id]
        return None

    def list_transfers(self) -> List[Transfer]:
        """
        Returns a snapshot of all transfer info.
        """
        return [self._cache[k] for k in self._cache]

    def list_ongoing(self) -> List[Transfer]:
        """
        Returns all ongoing transfers.
        """
        return [t for t in self.list_transfers() if not t.is_complete()]

    def list_completed(self) -> List[Transfer]:
        """
        Returns all completed transfers (successful or not).
        """
        return [t for t in self.list_transfers() if t.is_complete()]

    def _process(self, proto) -> Transfer:
        if proto.id in self._cache:
            transfer = self._cache[proto.id]
            transfer._proto = proto
        else:
            transfer = Transfer(proto, service_client=self.service_client)
            self._cache[transfer.id] = transfer

        return transfer


class FileListSubscription(WebSocketSubscriptionFuture):
    """
    Local object providing access to filelist updates.

    A subscription object stores the last filelist info for
    each remotepath and destination.
    """

    def __init__(self, manager):
        super(FileListSubscription, self).__init__(manager)
        self._cache = {}
        """Filelist cache keyed by (destination, remotePath)"""

    def get_filelist(
        self, remote_path: str, destination: str
    ) -> Optional[RemoteFileListing]:
        """
        Get the latest cached filelist for the given remote path and destination

        :param remote_path:
            path on the remote destination
        :param destination:
            remote entity name
        """
        return self._cache.get((remote_path, destination))

    def _process(self, proto) -> RemoteFileListing:
        filelist = RemoteFileListing(proto)
        self._cache[(filelist.destination, filelist.remote_path)] = filelist
        return filelist


class FileTransferClient:
    """
    Client for working with file transfers (e.g. CFDP) managed by Yamcs.
    """

    def __init__(self, ctx: Context, instance: str):
        super(FileTransferClient, self).__init__()
        self.ctx = ctx
        self._instance = instance
        self._default_service = None

    def list_services(self) -> Iterable[FileTransferService]:
        """
        List the services.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(path=f"/filetransfer/{self._instance}/services")
        message = filetransfer_pb2.ListFileTransferServicesResponse()
        message.ParseFromString(response.content)
        services = getattr(message, "services")
        result = []
        for proto in services:
            service_client = FileTransferServiceClient(self.ctx, proto)
            result.append(FileTransferService(proto, service_client))
        return iter(result)

    def get_service(self, name: str) -> FileTransferService:
        """
        Get a specific File Transfer service.

        :param name:
            The service name.
        """
        # TODO should have an actual server-side operation for this
        for service in self.list_services():
            if service.name == name:
                return service
        raise NotFound()


class FileTransferServiceClient:
    def __init__(self, ctx: Context, proto):
        self.ctx = ctx
        self._instance = proto.instance
        self._service = proto.name

    def upload(
        self,
        bucket_name: str,
        object_name: str,
        remote_path: str,
        source_entity: Optional[str],
        destination_entity: Optional[str],
        options: Optional[Mapping[str, Any]],
    ) -> Transfer:
        req = filetransfer_pb2.CreateTransferRequest()
        req.direction = filetransfer_pb2.TransferDirection.UPLOAD
        req.bucket = bucket_name
        req.objectName = object_name
        req.remotePath = remote_path
        if source_entity:
            req.source = source_entity
        if destination_entity:
            req.destination = destination_entity
        if options:
            req.options.update(options)

        url = f"/filetransfer/{self._instance}/{self._service}/transfers"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = filetransfer_pb2.TransferInfo()
        message.ParseFromString(response.content)
        return Transfer(message, self)

    def download(
        self,
        bucket_name: str,
        remote_path: str,
        object_name: Optional[str],
        source_entity: Optional[str],
        destination_entity: Optional[str],
        options: Optional[Mapping[str, Any]],
    ) -> Transfer:
        req = filetransfer_pb2.CreateTransferRequest()
        req.direction = filetransfer_pb2.TransferDirection.DOWNLOAD
        req.bucket = bucket_name
        req.remotePath = remote_path
        if object_name:
            req.objectName = object_name
        if source_entity:
            req.source = source_entity
        if destination_entity:
            req.destination = destination_entity
        if options:
            req.options.update(options)

        url = f"/filetransfer/{self._instance}/{self._service}/transfers"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = filetransfer_pb2.TransferInfo()
        message.ParseFromString(response.content)
        return Transfer(message, self)

    def fetch_filelist(
        self,
        remote_path: str,
        source_entity: Optional[str],
        destination_entity: Optional[str],
        options: Optional[Mapping[str, Any]],
    ):
        req = filetransfer_pb2.ListFilesRequest()
        req.remotePath = remote_path
        if source_entity:
            req.source = source_entity
        if destination_entity:
            req.destination = destination_entity
        if options:
            req.options.update(options)
        url = f"/filetransfer/{self._instance}/{self._service}/files:sync"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def get_filelist(
        self,
        remote_path: str,
        source_entity: Optional[str],
        destination_entity: Optional[str],
        options: Optional[Mapping[str, Any]],
    ) -> RemoteFileListing:
        params = {"remotePath": remote_path}
        if source_entity:
            params["source"] = source_entity
        if destination_entity:
            params["destination"] = destination_entity
        if options:
            params["options"] = json.dumps(options)
        url = f"/filetransfer/{self._instance}/{self._service}/files"
        response = self.ctx.get_proto(url, params=params)
        message = filetransfer_pb2.ListFilesResponse()
        message.ParseFromString(response.content)
        return RemoteFileListing(message)

    def pause_transfer(self, id: str) -> None:
        url = f"/filetransfer/{self._instance}/{self._service}/transfers/{id}:pause"
        self.ctx.post_proto(url)

    def resume_transfer(self, id: str) -> None:
        url = f"/filetransfer/{self._instance}/{self._service}/transfers/{id}:resume"
        self.ctx.post_proto(url)

    def cancel_transfer(self, id: str) -> None:
        url = f"/filetransfer/{self._instance}/{self._service}/transfers/{id}:cancel"
        self.ctx.post_proto(url)

    def run_file_action(
        self,
        file: str,
        action: str,
        message: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        req = filetransfer_pb2.RunFileActionRequest()
        req.file = file
        req.action = action
        if message:
            req.message.update(message)

        url = f"/filetransfer/{self._instance}/{self._service}/files:runFileAction"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        response_message = struct_pb2.Struct()
        response_message.ParseFromString(response.content)
        return json_format.MessageToDict(response_message)

    def create_transfer_subscription(
        self,
        on_data: Optional[Callable[[Transfer], None]] = None,
        timeout: float = 60,
    ) -> TransferSubscription:
        options = filetransfer_pb2.SubscribeTransfersRequest()
        options.instance = self._instance
        options.serviceName = self._service

        manager = WebSocketSubscriptionManager(
            self.ctx, topic="file-transfers", options=options
        )

        # Represent subscription as a future
        subscription = TransferSubscription(manager, self)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_transfer_data, subscription, on_data
        )

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def create_filelist_subscription(
        self,
        on_data: Optional[Callable[[RemoteFileListing], None]] = None,
        timeout: float = 60,
    ) -> FileListSubscription:
        options = filetransfer_pb2.SubscribeTransfersRequest()
        options.instance = self._instance
        options.serviceName = self._service

        manager = WebSocketSubscriptionManager(
            self.ctx, topic="remote-file-list", options=options
        )

        # Represent subscription as a future
        subscription = FileListSubscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_filelist_data, subscription, on_data
        )

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription
