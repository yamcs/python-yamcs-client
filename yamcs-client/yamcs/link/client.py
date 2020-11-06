import functools

from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.link.model import Cop1Config, Cop1Status
from yamcs.model import Link
from yamcs.protobuf.cop1 import cop1_pb2
from yamcs.protobuf.yamcsManagement import yamcsManagement_pb2


def _wrap_callback_parse_cop1_status(subscription, on_data, message):
    """
    Wraps a user callback to parse Cop1Status
    from a WebSocket data message
    """
    pb = cop1_pb2.Cop1Status()
    message.Unpack(pb)
    cop1_status = Cop1Status(pb)
    subscription._process(cop1_status)
    if on_data:
        on_data(cop1_status)


class Cop1Subscription(WebSocketSubscriptionFuture):
    """
    Local object providing access to COP1 status updates.
    """

    def __init__(self, manager):
        super(Cop1Subscription, self).__init__(manager)
        self._status = None

    def get_status(self):
        """
        Returns the latest known COP1 status.

        :rtype: .Cop1Status
        """
        return self._status

    @property
    def cop1_active(self):
        if self._status:
            return self._status.cop1_active
        return None

    @property
    def state(self):
        if self._status:
            return self._status.state
        return None

    @property
    def bypass_all(self):
        if self._status:
            return self._status.bypass_all
        return None

    @property
    def v_s(self):
        if self._status:
            return self._status.v_s
        return None

    @property
    def nn_r(self):
        if self._status:
            return self._status.nn_r
        return None

    def _process(self, update):
        self._status = update


class LinkClient:
    """Client object that groups operations for a specific link."""

    def __init__(self, ctx, instance, link):
        super(LinkClient, self).__init__()
        self.ctx = ctx
        self._instance = instance
        self._link = link

    def get_info(self):
        """
        Get info on this link.

        :rtype: .Link
        """
        response = self.ctx.get_proto(f"/links/{self._instance}/{self._link}")
        message = yamcsManagement_pb2.LinkInfo()
        message.ParseFromString(response.content)
        return Link(message)

    def enable_link(self):
        """
        Enables this link.
        """
        req = yamcsManagement_pb2.EditLinkRequest()
        req.state = "enabled"
        url = f"/links/{self._instance}/{self._link}"
        self.ctx.patch_proto(url, data=req.SerializeToString())

    def disable_link(self):
        """
        Disables this link.
        """
        req = yamcsManagement_pb2.EditLinkRequest()
        req.state = "disabled"
        url = f"/links/{self._instance}/{self._link}"
        self.ctx.patch_proto(url, data=req.SerializeToString())

    def get_cop1_config(self):
        """
        Gets the COP1 configuration for a data link.

        :rtype: .Cop1Config
        """
        response = self.ctx.get_proto(f"/cop1/{self._instance}/{self._link}/config")
        message = cop1_pb2.Cop1Config()
        message.ParseFromString(response.content)
        return Cop1Config(message)

    def update_cop1_config(
        self, window_width=None, timeout_type=None, tx_limit=None, t1=None,
    ):
        """
        Sets the COP1 configuration for a data link.

        :rtype: .Cop1Config
        """
        req = cop1_pb2.Cop1Config()
        if window_width is not None:
            req.windowWidth = window_width
        if timeout_type is not None:
            req.timeoutType = cop1_pb2.TimeoutType.Value(timeout_type)
        if tx_limit is not None:
            req.txLimit = tx_limit
        if t1 is not None:
            req.t1 = int(round(1000 * t1))

        url = f"/cop1/{self._instance}/{self._link}/config"
        response = self.ctx.patch_proto(url, data=req.SerializeToString())

        message = cop1_pb2.Cop1Config()
        message.ParseFromString(response.content)
        return Cop1Config(message)

    def disable_cop1(self, bypass_all=True):
        """
        Disable COP1 for a data link.

        :param bool bypass_all: All frames have bypass activated
                                (i.e. they will be BD frames)
        """
        req = cop1_pb2.DisableRequest()
        req.setBypassAll = bypass_all
        url = f"/cop1/{self._instance}/{self._link}:disable"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def initialize_cop1(self, type, clcw_wait_timeout=None, v_r=None):
        """
        Initialize COP1.

        :param str type: One of ``WITH_CLCW_CHECK``, ``WITHOUT_CLCW_CHECK``,
                         ``UNLOCK`` or ``SET_VR``
        :param int clcw_wait_timeout: timeout in seconds used for the reception of
                                      CLCW. Required if type is ``WITH_CLCW_CHECK``
        :param int v_r: value of v(R) if type is set to ``SET_VR``
        """
        req = cop1_pb2.InitializeRequest()
        req.type = cop1_pb2.InitializationType.Value(type)

        if clcw_wait_timeout is not None:
            req.clcwCheckInitializeTimeout = int(1000 * clcw_wait_timeout)
        if v_r is not None:
            req.vR = v_r

        url = f"/cop1/{self._instance}/{self._link}:initialize"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def resume_cop1(self):
        """
        Resume COP1.
        """
        req = cop1_pb2.ResumeRequest()
        url = f"/cop1/{self._instance}/{self._link}:resume"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def get_cop1_status(self):
        """
        Retrieve the COP1 status.

        :rtype: .Cop1Status
        """
        response = self.ctx.get_proto(f"/cop1/{self._instance}/{self._link}/status")
        message = cop1_pb2.Cop1Status()
        message.ParseFromString(response.content)
        return Cop1Status(message)

    def create_cop1_subscription(self, on_data, timeout=60):
        """
        Create a new subscription for receiving status of the COP1 link.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param on_data: Function that gets called on each :class:`.Cop1Status`.
        :type on_data: Optional[Callable[.Cop1Status])
        :param timeout: The amount of seconds to wait for the request to
                        complete.
        :type timeout: Optional[float]
        :return: Future that can be used to manage the background websocket
                 subscription.
        :rtype: .Cop1Subscription
        """
        options = cop1_pb2.SubscribeStatusRequest()
        options.instance = self._instance
        options.link = self._link

        manager = WebSocketSubscriptionManager(self.ctx, topic="cop1", options=options)

        # Represent subscription as a future
        subscription = Cop1Subscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_cop1_status, subscription, on_data
        )

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription
