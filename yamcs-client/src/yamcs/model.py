import warnings

warnings.warn(
    "The module 'yamcs.model' is deprecated. "
    "Import classes from 'yamcs.client' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from yamcs.client.model import (  # noqa
    AuthInfo,
    Event,
    Instance,
    InstanceTemplate,
    Link,
    LinkAction,
    LoadParameterValuesResult,
    ObjectPrivilege,
    Processor,
    RdbTablespace,
    ServerInfo,
    Service,
    UserInfo,
)
