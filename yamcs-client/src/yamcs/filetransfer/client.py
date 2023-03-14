import functools
import json

from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.filetransfer.model import RemoteFileListing, Service, Transfer
from yamcs.protobuf.filetransfer import filetransfer_pb2


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

    def __init__(self, manager, service_client):
        super(TransferSubscription, self).__init__(manager)
        self.service_client = service_client
        self._cache = {}
        """Transfer cache keyed by id."""

    def get_transfer(self, id):
        """
        Returns the latest transfer state.

        :param str id: Transfer identifier
        :rtype: .Transfer
        """
        if id in self._cache:
            return self._cache[id]
        return None

    def list_transfers(self):
        """
        Returns a snapshot of all transfer info.

        :rtype: .Transfer[]
        """
        return [self._cache[k] for k in self._cache]

    def list_ongoing(self):
        """
        Returns all ongoing transfers.

        :rtype: .Transfer[]
        """
        return [t for t in self.list_transfers() if not t.is_complete()]

    def list_completed(self):
        """
        Returns all completed transfers (successful or not).

        :rtype: .Transfer[]
        """
        return [t for t in self.list_transfers() if t.is_complete()]

    def _process(self, proto):
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

    def __init__(self, manager, service_client):
        super(FileListSubscription, self).__init__(manager)
        self.service_client = service_client
        self._cache = {}
        """Filelist cache keyed by (destination, remotePath)"""

    def get_filelist(self, remote_path, destination):
        """
        Get the latest cached filelist for the given remote path and destination
        :param remote_path: path on the remote destination
        :param destination: remote entity name
        :rtype .RemoteFileListing
        """
        return self._cache.get((remote_path, destination))

    def _process(self, filelist):
        filelist = RemoteFileListing(filelist)
        self._cache[(filelist.destination, filelist.remote_path)] = filelist
        return filelist


class FileTransferClient:
    """
    Client for working with file transfers (e.g. CFDP) managed by Yamcs.
    """

    def __init__(self, ctx, instance):
        super(FileTransferClient, self).__init__()
        self.ctx = ctx
        self._instance = instance
        self._default_service = None

    def list_services(self):
        """
        List the services.

        :rtype: ~collections.abc.Iterable[~yamcs.filetransfer.model.Service]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(path=f"/filetransfer/{self._instance}/services")
        message = filetransfer_pb2.ListFileTransferServicesResponse()
        message.ParseFromString(response.content)
        services = getattr(message, "services")
        result = []
        for proto in services:
            service_client = ServiceClient(self.ctx, proto)
            result.append(Service(proto, service_client))
        return iter(result)

    def get_service(self, name):
        """
        Get a specific File Transfer service.

        :param str name: The service name.
        :rtype: ~yamcs.filetransfer.model.Service
        """
        # TODO should have an actual server-side operation for this
        for service in self.list_services():
            if service.name == name:
                return service


class ServiceClient:
    def __init__(self, ctx, proto):
        self.ctx = ctx
        self._instance = proto.instance
        self._service = proto.name

    def upload(
        self,
        bucket_name,
        object_name,
        remote_path,
        source_entity,
        destination_entity,
        overwrite,
        parents,
        reliable,
        options,
    ):
        req = filetransfer_pb2.CreateTransferRequest()
        req.direction = filetransfer_pb2.TransferDirection.UPLOAD
        req.bucket = bucket_name
        req.objectName = object_name
        req.remotePath = remote_path
        if source_entity:
            req.source = source_entity
        if destination_entity:
            req.destination = destination_entity

        # Old options for backwards compatibility
        old_options = {
            "overwrite": overwrite,
            "createPath": parents,
            "reliable": reliable,
        }
        req.options.update(old_options)
        if options:
            req.options.update(options)

        url = f"/filetransfer/{self._instance}/{self._service}/transfers"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = filetransfer_pb2.TransferInfo()
        message.ParseFromString(response.content)
        return Transfer(message, self)

    def download(
        self,
        bucket_name,
        remote_path,
        object_name,
        source_entity,
        destination_entity,
        overwrite,
        parents,
        reliable,
        options,
    ):
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

        # Old options for backwards compatibility
        old_options = {
            "overwrite": overwrite,
            "createPath": parents,
            "reliable": reliable,
        }
        req.options.update(old_options)
        if options:
            req.options.update(options)

        url = f"/filetransfer/{self._instance}/{self._service}/transfers"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = filetransfer_pb2.TransferInfo()
        message.ParseFromString(response.content)
        return Transfer(message, self)

    def fetch_filelist(self, remote_path, source_entity, destination_entity, options):
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

    def get_filelist(self, remote_path, source_entity, destination_entity, options):
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

    def pause_transfer(self, id):
        url = f"/filetransfer/{self._instance}/{self._service}/transfers/{id}:pause"
        self.ctx.post_proto(url)

    def resume_transfer(self, id):
        url = f"/filetransfer/{self._instance}/{self._service}/transfers/{id}:resume"
        self.ctx.post_proto(url)

    def cancel_transfer(self, id):
        url = f"/filetransfer/{self._instance}/{self._service}/transfers/{id}:cancel"
        self.ctx.post_proto(url)

    def create_transfer_subscription(self, on_data=None, timeout=60):
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

    def create_filelist_subscription(self, on_data=None, timeout=60):
        options = filetransfer_pb2.SubscribeTransfersRequest()
        options.instance = self._instance
        options.serviceName = self._service

        manager = WebSocketSubscriptionManager(
            self.ctx, topic="remote-file-list", options=options
        )

        # Represent subscription as a future
        subscription = FileListSubscription(manager, self)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_filelist_data, subscription, on_data
        )

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription
