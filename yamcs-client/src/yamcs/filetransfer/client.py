import functools

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


def _wrap_callback_parse_filelist_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse TransferInfo
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
        """Filelist cache keyed by (destianation, remotePath)"""

    def get_filelist(self, remote_path, destination):
        return self._cache.get((remote_path, destination))

    def _process(self, filelist):
        self._cache[(filelist.destination, filelist.remotePath)] = filelist
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


def _get_options_for_deprecated(options):
    """
    Get the new options that match the deprecated ones by name (if any) from the list of new options.
    :param options: list of new FileTransferOptions.
    :return: array of matching (or Nones) createPath option, overwrite (parents) option, and reliable option.
    """
    overwrite_option = None
    create_path_option = None
    reliable_option = None
    for option in options:
        if option.name == 'overwrite':
            overwrite_option = option
        elif option.name == 'createPath':
            create_path_option = option
        elif option.name == 'reliable' or option.name == 'reliability':
            reliable_option = option
    return create_path_option, overwrite_option, reliable_option


def _get_old_options(overwrite, parents, reliable, deprecated_options):
    """
    Get as old options (overwrite, createPath, reliable) the values from the new options or the parameter's if None.
    :param overwrite: overwrite value from the deprecated signature.
    :param parents: parents value from the deprecated signature.
    :param reliable: reliable value from the deprecated signature.
    :param deprecated_options: array of new matching options (or Nones) as returned by _get_options_for_deprecated.
    :return: boolean values for the old UploadOptions/DownloadOptions.
    """
    return [
        overwrite if deprecated_options[0] is None else deprecated_options[0].booleanValue,
        parents if deprecated_options[1] is None else deprecated_options[1].booleanValue,
        reliable if deprecated_options[2] is None else deprecated_options[2].booleanValue
    ]


def _get_new_options(overwrite, parents, reliable, deprecated_options):
    """
    Get old options from the deprecated signature as new FileTransferOptions (not added if already present in dpeprecated_options).
    :param overwrite: overwrite value from the deprecated signature.
    :param parents: parents value from the deprecated signature.
    :param reliable: reliable value from the deprecated signature.
    :param deprecated_options: array of new matching options (or Nones) as returned by _get_options_for_deprecated.
    :return: list of FileTransferOptions got from the old values to add along the other new options
    """
    filetransfer_options = []
    if not deprecated_options[0]:
        filetransfer_options.append(create_filetransfer_option("overwrite", filetransfer_pb2.FileTransferOptionType.BOOLEAN, overwrite))
    if not deprecated_options[1]:
        filetransfer_options.append(create_filetransfer_option("createPath", filetransfer_pb2.FileTransferOptionType.BOOLEAN, parents))
    if not deprecated_options[2]:
        filetransfer_options.append(create_filetransfer_option("reliable", filetransfer_pb2.FileTransferOptionType.BOOLEAN, reliable))
    return filetransfer_options


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
        deprecated_options = _get_options_for_deprecated(options) if options else [None, None, None]
        req.uploadOptions.overwrite, req.uploadOptions.createPath, req.uploadOptions.reliable = _get_old_options(overwrite, parents, reliable, deprecated_options)
        # New options
        req.options.extend(_get_new_options(overwrite, parents, reliable, deprecated_options))
        if options:
            req.options.extend(options)
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
        deprecated_options = _get_options_for_deprecated(options) if options else [None, None, None]
        req.downloadOptions.overwrite, req.downloadOptions.createPath, req.downloadOptions.reliable = _get_old_options(overwrite, parents, reliable, deprecated_options)
        # New options
        req.options.extend(_get_new_options(overwrite, parents, reliable, deprecated_options))
        if options:
            req.options.extend(options)
        url = f"/filetransfer/{self._instance}/{self._service}/transfers"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = filetransfer_pb2.TransferInfo()
        message.ParseFromString(response.content)
        return Transfer(message, self)

    def fetch_filelist(self, remote_path, source_entity, destination_entity, reliable):
        req = filetransfer_pb2.ListFilesRequest()
        req.remotePath = remote_path
        if source_entity:
            req.source = source_entity
        if destination_entity:
            req.destination = destination_entity
        req.reliable = reliable
        url = f"/filetransfer/{self._instance}/{self._service}/files:sync"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def get_filelist(self, remote_path, source_entity, destination_entity, reliable):
        params = {
            "remotePath": remote_path,
            "reliable": reliable
        }
        if source_entity:
            params["source"] = source_entity
        if destination_entity:
            params["destination"] = destination_entity
        url = f"/filetransfer/{self._instance}/{self._service}/files"
        response = self.ctx.get_proto(url, params=params)
        message = filetransfer_pb2.ListFilesResponse()
        message.ParseFromString(response.content)
        return message

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


def create_filetransfer_option(name, option_type, value):
    """
    Create a FileTransferOption object to put into upload/download options array parameter
    :param name: name identifier of the option
    :param option_type: type of option
    :param value: value of the option
    :return: FileTransferOption (protobuf) object with given name, type and value
    """
    option = filetransfer_pb2.FileTransferOption()
    option.name = name
    option.type = option_type
    if option_type == filetransfer_pb2.FileTransferOptionType.BOOLEAN:
        option.booleanValue = value
    elif option_type == filetransfer_pb2.FileTransferOptionType.DOUBLE:
        option.doubleValues.append(value)
    elif option_type == filetransfer_pb2.FileTransferOptionType.STRING:
        string_value = filetransfer_pb2.StringValue()
        string_value.value = value
        option.stringValues.append(string_value)
    return option
