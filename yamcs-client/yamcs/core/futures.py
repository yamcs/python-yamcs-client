import abc
import threading

from yamcs.core.exceptions import TimeoutError, YamcsError


class Future(object):

    """Future for capturing asynchronous execution.

    This interface is based on :class:`concurrent.futures.Future` available in Python 3 (not
    in Python 2).
    """

    @abc.abstractmethod
    def cancel(self):
        """
        Attempt to cancel the call. If the call is currently being executed and
        cannot be cancelled then the method will return False, otherwise the call
        will be cancelled and the method will return True.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def cancelled(self):
        """Return True if the call was successfully cancelled."""
        raise NotImplementedError()

    @abc.abstractmethod
    def running(self):
        """Return True if the call is currently being executed and cannot be cancelled."""
        raise NotImplementedError()

    @abc.abstractmethod
    def done(self):
        """Return True if the call was successfully cancelled or finished running."""
        raise NotImplementedError()

    @abc.abstractmethod
    def result(self, timeout=None):
        """
        Return the value returned by the call. If the call hasn't yet completed then
        this method will wait up to timeout seconds. If the call hasn't completed in
        timeout seconds, then a :class`TimeoutError` will be raised.
        timeout can be an int or float. If timeout is not specified or None, there
        is no limit to the wait time.

        If the future is cancelled before completing then CancelledError will be
        raised.

        If the call raised, this method will raise the same exception.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def exception(self, timeout=None):
        """
        Return the exception raised by the call. If the call hasn't yet completed
        then this method will wait up to timeout seconds. If the call hasn't
        completed in timeout seconds, then a :class`TimeoutError` will
        be raised. timeout can be an int or float. If timeout is not specified or
        None, there is no limit to the wait time.

        If the future is cancelled before completing then CancelledError will be
        raised.

        If the call completed without raising, None is returned.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def add_done_callback(self, fn):
        """
        Attaches the callable fn to the future. fn will be called, with the future
        as its only argument, when the future is cancelled or finishes running.

        Added callables are called in the order that they were added and are always
        called in a thread belonging to the process that added them. If the
        callable raises an Exception subclass, it will be logged and ignored. If
        the callable raises a BaseException subclass, the behavior is undefined.

        If the future has already completed or been cancelled, fn will be called
        immediately.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def set_result(self, result):
        """Sets the result of the work associated with the Future to result."""
        raise NotImplementedError()

    @abc.abstractmethod
    def set_exception(self, exception):
        """Sets the result of the work associated with the Future to the exception."""
        raise NotImplementedError()


class WebSocketSubscriptionFuture(Future):
    """
    Future for capturing the asynchronous execution of a WebSocket subscription.
    """

    def __init__(self, manager):
        super(WebSocketSubscriptionFuture, self).__init__()
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
                target=self._manager.close,
                kwargs={'reason': exception},
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
        return (self._exception is not None or
                self._result is not None)

    def reply(self, timeout=None):
        """
        Returns the initial reply. This is emitted before any subscription
        data is emitted. This function raises an exception if the subscription
        attempt failed.
        """
        self._wait_on_signal(self._response_received)
        if self._response_exception is not None:
            msg = self._response_exception.message
            raise YamcsError(msg)
        return self._response_reply

    # pylint: disable-msg=E0702
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
        # Wait until the future is done. We do not use wait() without timeout
        # because on Python 2.x this does not generate ``KeyboardInterrupt``.
        # https://bugs.python.org/issue8844
        if timeout is not None:
            if not event.wait(timeout=timeout):
                # Remark that a timeout does *not* mean that the underlying
                # work is canceled.
                raise TimeoutError('Timed out.')
        else:
            # The actual timeout value does not have any impact
            while not event.wait(timeout=10):
                pass  # tick

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
