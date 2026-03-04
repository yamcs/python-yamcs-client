import warnings

warnings.warn(
    "The module 'yamcs.tmtc.model' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.tmtc.model import (  # noqa
    Acknowledgment,
    Alarm,
    AlarmRangeSet,
    AlarmUpdate,
    Calibrator,
    CommandHistory,
    ContainerData,
    EventAlarm,
    IssuedCommand,
    MonitoredCommand,
    Packet,
    ParameterAlarm,
    ParameterData,
    ParameterValue,
    ValueUpdate,
    VerificationConfig,
)

RangeSet = AlarmRangeSet
"""
Temporary backwards compatibility.
Prefer to use the class 'AlarmRangeSet'.
"""
