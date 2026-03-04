import warnings

warnings.warn(
    "The module 'yamcs.link.client' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.links.client import Cop1Subscription, LinkClient  # noqa
