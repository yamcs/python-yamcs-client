class YamcsError(Exception):
    """Base class for raised exceptions."""
    pass


class ConnectionFailure(YamcsError):
    """Yamcs is not or no longer available."""
    pass


class TimeoutError(YamcsError):
    """The operation exceeded the given deadline."""
    pass


class NotFound(YamcsError):
    """The resource was not found."""
    pass

class Unauthorized(YamcsError):
    """Unable to get access the resource."""
    pass
