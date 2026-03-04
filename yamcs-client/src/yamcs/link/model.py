import warnings

warnings.warn(
    "The module 'yamcs.link.model' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.links.model import Cop1Config, Cop1Status  # noqa
