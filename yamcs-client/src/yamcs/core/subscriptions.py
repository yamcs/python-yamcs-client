import logging
import ssl
import threading

import websocket
from yamcs.api import websocket_pb2
from yamcs.core.exceptions import ConnectionFailure


class WebSocketSubscriptionManager:
    def __init__(self, ctx, topic, options=None):
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
        if not self.ctx.session.verify:
            kwargs["sslopt"] = {"cert_reqs": ssl.CERT_NONE}

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
        self._websocket.send(frame_data, websocket.ABNF.OPCODE_BINARY)

    def _on_websocket_open(self, ws):
        self.send(self._options)

    def _on_websocket_message(self, ws, message):
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
                self._callback(data)
        except Exception as e:
            logging.exception("Problem while processing message. Closing connection")
            self._close_async(reason=e)

    def _on_websocket_error(self, ws, error):
        logging.exception("WebSocket error")

        # Generate our own exception.
        # (the default message is misleading 'connection is already closed')
        if isinstance(error, websocket.WebSocketConnectionClosedException):
            error = ConnectionFailure("Connection closed")

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
