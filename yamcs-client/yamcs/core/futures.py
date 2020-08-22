import threading
from concurrent.futures import Future

from yamcs.core.exceptions import TimeoutError, YamcsError


class WebSocketSubscriptionFuture(Future):
    """
    Future for capturing the asynchronous execution of a WebSocket subscription.
    """

    def __init__(self, manager):
        super(WebSocketSubscriptionFuture, self).__init__()
        self.ctx = manager.ctx
        self._manager = manager
        self._manager.add_response_callback(self._on_response_callback)
        self._manager.add_close_callback(self._on_close_callback)

        # Yamcs send either a 'reply' message or an 'exception' message on
        # every websocket subscription. If the ``_response_received`` event
        # is set it means either of these two has arrived.
        self._response_received = threading.Event()
        self._response_reply = None
        self._response_exception = None

        self._result = None
        self._exception = None
        self._callbacks = []

        self._completed = threading.Event()
        self._cancelled = False

    def _on_response_callback(self, manager, reply=None, exception=None):
        self._response_reply = reply
        self._response_exception = exception
        self._response_received.set()

        # Yamcs leaves the socket open because it was designed with
        # multiple parallel subscriptions in mind. We don't use this
        # notion, so close the connection.
        if exception:
            closer = threading.Thread(
                target=self._manager.close, kwargs={"reason": exception},
            )
            closer.daemon = True
            closer.start()

    def _on_close_callback(self, manager, result):
        if result is None:
            self.set_result(True)
        else:
            self.set_exception(result)

    def cancel(self):
        """
        Closes the websocket and shutdowns the background thread consuming
        messages.
        """
        self._cancelled = True
        return self._manager.close()

    def cancelled(self):
        return self._cancelled

    def running(self):
        if self.done():
            return False
        return True

    def done(self):
        # We're assuming that None cannot be a valid result
        return self._exception is not None or self._result is not None

    def reply(self, timeout=None):
        """
        Returns the initial reply. This is emitted before any subscription
        data is emitted. This function raises an exception if the subscription
        attempt failed.
        """
        self._wait_on_signal(self._response_received)
        if self._response_exception is not None:
            msg = self._response_exception.msg
            raise YamcsError(msg)
        return self._response_reply

    def result(self, timeout=None):
        err = self.exception(timeout=timeout)
        if err is None:
            return self._result
        raise err

    def exception(self, timeout=None):
        self._wait_on_signal(self._completed, timeout)

        if self._result is not None:
            return None

        return self._exception

    def _wait_on_signal(self, event, timeout=None):
        if not event.wait(timeout=timeout):
            # Remark that a timeout does *not* mean that the underlying
            # work is canceled.
            raise TimeoutError("Timed out.")

    def add_done_callback(self, fn):
        if self.done():
            fn(self)
        self._callbacks.append(fn)

    def set_result(self, result):
        assert not self.done()

        self._result = result
        self._completed.set()
        for callback in self._callbacks:
            callback(self)

    def set_exception(self, exception):
        assert not self.done()

        self._exception = exception
        self._completed.set()
        for callback in self._callbacks:
            callback(self)
