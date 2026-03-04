import warnings

warnings.warn(
    "The module 'yamcs.tmtc.client' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.tmtc.client import (  # noqa
    AlarmSubscription,
    CommandConnection,
    CommandHistorySubscription,
    ContainerSubscription,
    ParameterSubscription,
    ProcessorClient,
)
