import warnings

warnings.warn(
    "The module 'yamcs.mdb.model' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.mdb.model import (  # noqa
    Algorithm,
    Argument,
    ArgumentType,
    ArrayType,
    Command,
    Container,
    DataEncoding,
    EnumValue,
    Member,
    MissionDatabaseItem,
    Parameter,
    ParameterType,
    RangeSet,
    Significance,
    SpaceSystem,
)
