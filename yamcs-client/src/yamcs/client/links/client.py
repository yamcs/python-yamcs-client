import functools
from typing import Any, Callable, Dict, Mapping, Optional

from google.protobuf import json_format, struct_pb2
from yamcs.client.core.context import Context
from yamcs.client.core.futures import WebSocketSubscriptionFuture
from yamcs.client.core.subscriptions import WebSocketSubscriptionManager
from yamcs.client.links.model import Cop1Config, Cop1Status
from yamcs.client.model import Link
from yamcs.protobuf.cop1 import cop1_pb2
from yamcs.protobuf.links import links_pb2

__all__ = [
    "Cop1Subscription",
    "LinkClient",
]


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

    def get_status(self) -> Optional[Cop1Status]:
        """
        Returns the latest known COP1 status.
        """
        return self._status

    @property
    def cop1_active(self) -> Optional[bool]:
        if self._status:
            return self._status.cop1_active
        return None

    @property
    def state(self) -> Optional[str]:
        if self._status:
            return self._status.state
        return None

    @property
    def bypass_all(self) -> Optional[bool]:
        if self._status:
            return self._status.bypass_all
        return None

    @property
    def v_s(self) -> Optional[int]:
        if self._status:
            return self._status.v_s
        return None

    @property
    def nn_r(self) -> Optional[int]:
        if self._status:
            return self._status.nn_r
        return None

    def _process(self, update):
        self._status = update


class LinkClient:
    """Client object that groups operations for a specific link."""

    def __init__(self, ctx: Context, instance: str, link: str):
        super(LinkClient, self).__init__()
        self.ctx = ctx
        self._instance = instance
        self._link = link

    def get_info(self) -> Link:
        """
        Get info on this link.
        """
        response = self.ctx.get_proto(f"/links/{self._instance}/{self._link}")
        message = links_pb2.LinkInfo()
        message.ParseFromString(response.content)
        return Link(message)

    def enable_link(self):
        """
        Enables this link.
        """
        req = links_pb2.EnableLinkRequest()
        url = f"/links/{self._instance}/{self._link}:enable"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def disable_link(self):
        """
        Disables this link.
        """
        req = links_pb2.DisableLinkRequest()
        url = f"/links/{self._instance}/{self._link}:disable"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def run_action(
        self,
        action: str,
        message: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Runs the given action for this link

        :param action:
            action identifier
        :param message:
            action message
        :return:
            Action result (if the action returns anything)
        """
        req = links_pb2.RunActionRequest()
        if message:
            req.message.update(message)

        url = f"/links/{self._instance}/{self._link}/actions/{action}"
        response = self.ctx.post_proto(url, data=req.message.SerializeToString())
        response_message = struct_pb2.Struct()
        response_message.ParseFromString(response.content)
        return json_format.MessageToDict(response_message)

    def get_cop1_config(self) -> Cop1Config:
        """
        Gets the COP1 configuration for a data link.
        """
        response = self.ctx.get_proto(f"/cop1/{self._instance}/{self._link}/config")
        message = cop1_pb2.Cop1Config()
        message.ParseFromString(response.content)
        return Cop1Config(message)

    def update_cop1_config(
        self,
        window_width: Optional[int] = None,
        timeout_type: Optional[str] = None,
        tx_limit: Optional[int] = None,
        t1: Optional[float] = None,
    ) -> Cop1Config:
        """
        Sets the COP1 configuration for a data link.
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

    def disable_cop1(self, bypass_all: bool = True):
        """
        Disable COP1 for a data link.

        :param bypass_all:
            All frames have bypass activated (i.e. they will be BD frames)
        """
        req = cop1_pb2.DisableRequest()
        req.setBypassAll = bypass_all
        url = f"/cop1/{self._instance}/{self._link}:disable"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def initialize_cop1(
        self,
        type: str,
        clcw_wait_timeout: Optional[int] = None,
        v_r: Optional[int] = None,
    ):
        """
        Initialize COP1.

        :param type:
            One of ``WITH_CLCW_CHECK``, ``WITHOUT_CLCW_CHECK``,
            ``UNLOCK`` or ``SET_VR``
        :param clcw_wait_timeout:
            timeout in seconds used for the reception of
            CLCW. Required if type is ``WITH_CLCW_CHECK``
        :param v_r:
            value of v(R) if type is set to ``SET_VR``
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

    def get_cop1_status(self) -> Cop1Status:
        """
        Retrieve the COP1 status.
        """
        response = self.ctx.get_proto(f"/cop1/{self._instance}/{self._link}/status")
        message = cop1_pb2.Cop1Status()
        message.ParseFromString(response.content)
        return Cop1Status(message)

    def create_cop1_subscription(
        self, on_data: Callable[[Cop1Status], None], timeout: float = 60
    ) -> Cop1Subscription:
        """
        Create a new subscription for receiving status of the COP1 link.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param on_data:
            Function that gets called on each :class:`.Cop1Status`.
        :param timeout:
            The amount of seconds to wait for the request to complete.
        :return:
            Future that can be used to manage the background websocket
            subscription.
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
