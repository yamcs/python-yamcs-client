import warnings

warnings.warn(
    "The module 'yamcs.timeline' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.timeline.client import TimelineClient  # noqa
