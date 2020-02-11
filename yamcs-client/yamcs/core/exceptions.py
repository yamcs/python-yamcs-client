class YamcsError(Exception):
    """Base class for raised exceptions."""


class ConnectionFailure(YamcsError):
    """Yamcs is not or no longer available."""


class TimeoutError(YamcsError):
    """The operation exceeded the given deadline."""


class NotFound(YamcsError):
    """The resource was not found."""


class Unauthorized(YamcsError):
    """Unable to get access the resource."""
