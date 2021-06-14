import functools
import warnings

from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.filetransfer.model import Service, Transfer
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

    def list_transfers(self):
        """
        Deprecated. Use ``get_service(service).list_transfers()``.
        """
        warnings.warn(
            "Use a specific service: get_service(service).list_transfers()",
            FutureWarning,
        )
        if not self._default_service:
            self._default_service = next(self.list_services(), None)

        return self._default_service.list_transfers()

    def get_transfer(self, id):
        """
        Deprecated. Use ``get_service(service).get_transfer(id)``.
        """
        warnings.warn(
            "Use a specific service: get_service(service).get_transfer(id)",
            FutureWarning,
        )
        if not self._default_service:
            self._default_service = next(self.list_services(), None)

        return self._default_service.get_transfer(id)

    def upload(self, *args, **kwargs):
        """
        Deprecated. Use ``get_service(service).upload(...)``.
        """
        warnings.warn(
            "Use a specific service: get_service(service).upload(...)", FutureWarning,
        )
        if not self._default_service:
            self._default_service = next(self.list_services(), None)

        return self._default_service.upload(*args, **kwargs)

    def pause_transfer(self, id):
        """
        Deprecated. Use ``get_service(service).pause_transfer(id)``.
        """
        warnings.warn(
            "Use a specific service: get_service(service).pause_transfer(id)",
            FutureWarning,
        )
        if not self._default_service:
            self._default_service = next(self.list_services(), None)

        return self._default_service.pause_transfer(id)

    def resume_transfer(self, id):
        """
        Deprecated. Use ``get_service(service).resume_transfer(id)``.
        """
        warnings.warn(
            "Use a specific service: get_service(service).resume_transfer(id)",
            FutureWarning,
        )
        if not self._default_service:
            self._default_service = next(self.list_services(), None)

        return self._default_service.resume_transfer(id)

    def cancel_transfer(self, id):
        """
        Deprecated. Use ``get_service(service).cancel_transfer(id)``.
        """
        warnings.warn(
            "Use a specific service: get_service(service).cancel_transfer(id)",
            FutureWarning,
        )
        if not self._default_service:
            self._default_service = next(self.list_services(), None)

        return self._default_service.cancel_transfer(id)

    def create_transfer_subscription(self, *args, **kwargs):
        """
        Deprecated. Use ``get_service(service).create_transfer_subscription(...)``.
        """
        warnings.warn(
            "Use a specific service: "
            "get_service(service).create_transfer_subscription(...)",
            FutureWarning,
        )
        if not self._default_service:
            self._default_service = next(self.list_services(), None)
        return self._default_service.create_transfer_subscription(*args, **kwargs)


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
        req.uploadOptions.overwrite = overwrite
        req.uploadOptions.createPath = parents
        req.uploadOptions.reliable = reliable
        url = f"/filetransfer/{self._instance}/{self._service}/transfers"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = filetransfer_pb2.TransferInfo()
        message.ParseFromString(response.content)
        return Transfer(message, self)

    def download(
        self,
        bucket_name,
        object_name,
        remote_path,
        source_entity,
        destination_entity,
        overwrite,
        parents,
        reliable,
    ):
        req = filetransfer_pb2.CreateTransferRequest()
        req.direction = filetransfer_pb2.TransferDirection.DOWNLOAD
        req.bucket = bucket_name
        req.objectName = object_name
        req.remotePath = remote_path
        if source_entity:
            req.source = source_entity
        if destination_entity:
            req.destination = destination_entity
        req.uploadOptions.overwrite = overwrite
        req.uploadOptions.createPath = parents
        req.uploadOptions.reliable = reliable
        url = f"/filetransfer/{self._instance}/{self._service}/transfers"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = filetransfer_pb2.TransferInfo()
        message.ParseFromString(response.content)
        return Transfer(message, self)

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
