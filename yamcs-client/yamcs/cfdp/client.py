import functools

from yamcs.cfdp.model import Transfer
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.protobuf.cfdp import cfdp_pb2


def _wrap_callback_parse_transfer_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse TransferInfo
    from a WebSocket data message
    """
    pb = cfdp_pb2.TransferInfo()
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

    def __init__(self, manager, cfdp_client):
        super(TransferSubscription, self).__init__(manager)
        self.cfdp_client = cfdp_client
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
            transfer = Transfer(proto, cfdp_client=self.cfdp_client)
            self._cache[transfer.id] = transfer

        return transfer


class CFDPClient:
    """
    Client for working with CFDP transfers managed by Yamcs.
    """

    def __init__(self, ctx, instance):
        super(CFDPClient, self).__init__()
        self.ctx = ctx
        self._instance = instance

    def list_transfers(self):
        """
        List the transfers.

        :rtype: ~collections.Iterable[.Transfer]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(path="/cfdp/" + self._instance + "/transfers")
        message = cfdp_pb2.ListTransfersResponse()
        message.ParseFromString(response.content)
        transfers = getattr(message, "transfers")
        return iter([Transfer(transfer, self) for transfer in transfers])

    def get_transfer(self, id):
        """
        Get a specific transfer.

        :rtype: .Transfer
        """
        url = "/cfdp/{}/transfers/{}".format(self._instance, id)
        response = self.ctx.get_proto(url)
        message = cfdp_pb2.TransferInfo()
        message.ParseFromString(response.content)
        return Transfer(message, self)

    def upload(
        self,
        bucket_name,
        object_name,
        remote_path,
        overwrite=True,
        parents=True,
        reliable=False,
    ):
        """
        Uploads a file located in a bucket to a remote destination path.

        :param str bucket_name: Name of the bucket containing the source object.
        :param str object_name: Name of the source object.
        :param str remote_path: Remote destination.
        :param bool overwrite: Replace a destination if it already exists.
        :param bool parents: Create the remote path if it does not yet exist.
        :param bool reliable: Whether to use a Class 2 CFDP transfer.
        :rtype: .Transfer
        """
        req = cfdp_pb2.CreateTransferRequest()
        req.direction = cfdp_pb2.TransferDirection.UPLOAD
        req.bucket = bucket_name
        req.objectName = object_name
        req.remotePath = remote_path
        req.uploadOptions.overwrite = overwrite
        req.uploadOptions.createPath = parents
        req.uploadOptions.reliable = reliable
        url = "/cfdp/{}/transfers".format(self._instance)
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = cfdp_pb2.TransferInfo()
        message.ParseFromString(response.content)
        return Transfer(message, self)

    def pause_transfer(self, id):
        """
        Pauses a transfer
        """
        url = "/cfdp/{}/transfers/{}:pause".format(self._instance, id)
        self.ctx.post_proto(url)

    def resume_transfer(self, id):
        """
        Resume a transfer
        """
        url = "/cfdp/{}/transfers/{}:resume".format(self._instance, id)
        self.ctx.post_proto(url)

    def cancel_transfer(self, id):
        """
        Cancel a transfer
        """
        url = "/cfdp/{}/transfers/{}:cancel".format(self._instance, id)
        self.ctx.post_proto(url)

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
        options = cfdp_pb2.SubscribeTransfersRequest()
        options.instance = self._instance

        manager = WebSocketSubscriptionManager(
            self.ctx, topic="cfdp-transfers", options=options
        )

        # Represent subscription as a future
        subscription = TransferSubscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_transfer_data, subscription, on_data
        )

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription
