import warnings

warnings.warn(
    "The module 'yamcs.archive.model' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.archive.model import (  # noqa
    ColumnData,
    IndexGroup,
    IndexRecord,
    ParameterRange,
    ParameterRangeEntry,
    ResultSet,
    Sample,
    Stream,
    StreamData,
    Table,
)
