import warnings

warnings.warn(
    "The module 'yamcs.timeline.model' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.timeline.model import (  # noqa
    Band,
    CommandBand,
    Item,
    ItemBand,
    Spacer,
    TimeRuler,
    View,
)
