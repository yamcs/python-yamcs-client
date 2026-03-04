import warnings

warnings.warn(
    "The module 'yamcs.tco.model' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.tco.model import (  # noqa
    TCOCoefficients,
    TCOSample,
    TCOStatus,
    TofInterval,
)
