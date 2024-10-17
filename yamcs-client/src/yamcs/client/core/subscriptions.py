import logging
import ssl
import threading

import websocket
from yamcs.api import websocket_pb2
from yamcs.client.core.context import Context
from yamcs.client.core.exceptions import ConnectionFailure

__all__ = [
    "WebSocketSubscriptionManager",
]

logger = logging.getLogger("yamcs-client")


class WebSocketSubscriptionManager:
    def __init__(self, ctx: Context, topic: str, options=None):
        self.ctx = ctx
        self._topic = topic
        self._options = options

        self._websocket = None
        self._callback = None
        self._response_callbacks = []
        self._close_callbacks = []

        self._closing = threading.Lock()
        self._closed = False
        """True if this manager has already been closed."""

        self._request_counter = 0
        self._request_counter_lock = threading.Lock()
        self._call = None
        self._call_assigned = threading.Event()

        # Thread created in ``.open()``
        self._consumer = None

    def add_response_callback(self, callback):
        """
        Schedules a callable when a response was received.
        """
        self._response_callbacks.append(callback)

    def add_close_callback(self, callback):
        """
        Schedules a callable when the manager closes.
        """
        self._close_callbacks.append(callback)

    def open(self, callback):
        """
        Begin consuming messages.
        """
        assert not self._closed

        if self.ctx.credentials:
            self.ctx.credentials.before_request(self.ctx.session, self.ctx.auth_root)

        self._callback = callback
        self._websocket = websocket.WebSocketApp(
            self.ctx.ws_root,
            on_open=self._on_websocket_open,
            on_message=self._on_websocket_message,
            on_error=self._on_websocket_error,
            subprotocols=["protobuf"],
            header=[
                f"{k}: {self.ctx.session.headers[k]}" for k in self.ctx.session.headers
            ],
        )

        kwargs = {}
        if self.ctx.session.verify is False:
            kwargs["sslopt"] = {"cert_reqs": ssl.CERT_NONE}
        elif self.ctx.session.verify is not True:
            kwargs["sslopt"] = {"ca_certs": self.ctx.session.verify}

        self._consumer = threading.Thread(
            target=self._websocket.run_forever, kwargs=kwargs
        )

        # Running this as a daemon thread improves possibilities for consumers
        # of our API to control shutdown. For example can can just use
        # time.sleep on the main thread instead of blocking on the future.
        self._consumer.daemon = True

        self._consumer.start()

    def close(self, reason=None):
        """
        Stop consuming messages and perform an orderly shutdown.

        If ``reason`` is None, then this is considered a regular close.
        """
        with self._closing:
            if self._closed:
                return

            assert self._websocket is not None
            assert self._consumer is not None

            self._websocket.close()

            self._consumer.join()
            self._consumer = None

            self._websocket = None
            self._closed = True
            for cb in self._close_callbacks:
                cb(self, reason)

    def send(self, options=None):
        message = websocket_pb2.ClientMessage()
        message.type = self._topic

        # Ensure the server has already replied to the
        # previous message. (we want to be sure we know
        # our server-assigned call already)
        if self._request_counter > 0:
            if self._call is None:
                self._call_assigned.wait()
                assert self._call is not None
            message.call = self._call

        message.id = self._next_sequence_number()
        if options:
            getattr(message, "options").Pack(options)

        frame_data = message.SerializeToString()

        assert self._websocket is not None
        self._websocket.send(frame_data, websocket.ABNF.OPCODE_BINARY)

    def _on_websocket_open(self, ws=None):
        # WebSocketApp ``on_open`` callbacks had a temporary signature
        # change between websocket-client 0.48.0..0.57.0, hence we make
        # the ``ws`` argument optional.
        # https://github.com/websocket-client/websocket-client/issues/669
        #
        # This workaround can be dropped once we force websocket-client
        # to be >0.57
        self.send(self._options)

    def _on_websocket_message(self, ws, message=None):
        # WebSocketApp ``on_message`` callbacks had a temporary signature
        # change between websocket-client 0.48.0..0.57.0.
        # https://github.com/websocket-client/websocket-client/issues/669
        #
        # This workaround can be dropped once we force websocket-client
        # to be >0.57
        if message is None:
            message = ws

        try:
            pb2_message = websocket_pb2.ServerMessage()
            pb2_message.ParseFromString(message)

            type_ = getattr(pb2_message, "type")
            if type_ == "reply":
                reply = websocket_pb2.Reply()
                getattr(pb2_message, "data").Unpack(reply)
                if reply.HasField("exception"):
                    for cb in self._response_callbacks:
                        cb(self, exception=getattr(reply, "exception"))
                else:
                    if self._call is None:
                        self._call = getattr(pb2_message, "call")
                        self._call_assigned.set()
                    for cb in self._response_callbacks:
                        cb(self)
            else:
                data = getattr(pb2_message, "data")

                assert self._callback is not None
                self._callback(data)
        except Exception as e:
            logger.exception("Problem while processing message. Closing connection")
            self._close_async(reason=e)

    def _on_websocket_error(self, ws, error=None):
        # WebSocketApp ``on_error`` callbacks had a temporary signature
        # change between websocket-client 0.48.0..0.57.0.
        # https://github.com/websocket-client/websocket-client/issues/669
        #
        # This workaround can be dropped once we force websocket-client
        # to be >0.57
        if error is None:
            error = ws

        # Set to False to avoid printing some errors twice
        # (the ones that are generated during an initial connection)
        log_error = True

        # Generate custom exception.
        # (the default message is misleading 'connection is already closed')
        if isinstance(error, websocket.WebSocketConnectionClosedException):
            error = ConnectionFailure("Connection closed")
        elif isinstance(error, websocket.WebSocketAddressException):
            # No log because this error usually happens while blocking on an
            # initial connection, so prefer not to print it twice.
            log_error = False
            msg = f"Connection to {self.ctx.url} failed: could not resolve hostname"
            error = ConnectionFailure(msg)
        elif isinstance(error, ConnectionRefusedError):
            log_error = False
            msg = f"Connection to {self.ctx.url} failed: connection refused"
            error = ConnectionFailure(msg)

        if log_error:
            logger.error("WebSocket error: %s", error)

        self._close_async(reason=error)

    def _close_async(self, reason):
        # Close async. This is to not get stuck in the above ``join()``.
        closer = threading.Thread(target=self.close, kwargs={"reason": reason})
        closer.daemon = True
        closer.start()

    def _next_sequence_number(self):
        with self._request_counter_lock:
            self._request_counter += 1
            return self._request_counter
