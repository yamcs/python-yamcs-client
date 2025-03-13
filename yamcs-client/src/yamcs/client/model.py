import datetime
from typing import Any, Dict, List, Optional

from yamcs.client.core.helpers import parse_server_time
from yamcs.protobuf.events import events_pb2
from yamcs.protobuf.instances import instances_pb2
from yamcs.protobuf.services import services_pb2

__all__ = [
    "AuthInfo",
    "Event",
    "Instance",
    "InstanceTemplate",
    "Link",
    "LinkAction",
    "LoadParameterValuesResult",
    "ObjectPrivilege",
    "Processor",
    "RdbTablespace",
    "ServerInfo",
    "Service",
    "UserInfo",
]


class AuthInfo:
    """
    Authentication information
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def require_authentication(self) -> bool:
        return self._proto.requireAuthentication


class ServerInfo:
    """
    General server properties.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def id(self) -> str:
        """The Server ID."""
        return self._proto.serverId

    @property
    def version(self) -> str:
        """The version of Yamcs Server."""
        return self._proto.yamcsVersion

    @property
    def default_yamcs_instance(self) -> Optional[str]:
        """Returns the default Yamcs instance."""
        if self._proto.HasField("defaultYamcsInstance"):
            return self._proto.defaultYamcsInstance
        return None

    def __str__(self):
        return f"{self.id} (v{self.version})"


class UserInfo:
    """
    Info on a Yamcs User.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def username(self) -> str:
        return self._proto.name

    @property
    def superuser(self) -> bool:
        return self._proto.superuser

    @property
    def system_privileges(self) -> List[str]:
        return [p for p in self._proto.systemPrivileges]

    @property
    def object_privileges(self) -> List["ObjectPrivilege"]:
        return [ObjectPrivilege(p) for p in self._proto.objectPrivileges]

    def __str__(self):
        return self.username


class ObjectPrivilege:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        return self._proto.type

    @property
    def objects(self) -> List[str]:
        return [o for o in self._proto.objects]

    def __str__(self):
        return self.name


class Event:
    """
    A timetagged free-text message. Events work a lot like log
    messages in logging frameworks, but then targeted at operators.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def generation_time(self) -> datetime.datetime:
        """
        The time when the event was generated.
        """
        return parse_server_time(self._proto.generationTime)

    @property
    def reception_time(self) -> datetime.datetime:
        """
        The time when the event was received by Yamcs.
        """
        return parse_server_time(self._proto.receptionTime)

    @property
    def severity(self) -> Optional[str]:
        """
        Severity level of the event. One of ``INFO``, ``WATCH``,
        ``WARNING``, ``DISTRESS``, ``CRITICAL`` or ``SEVERE``.
        """
        if self._proto.HasField("severity"):
            name = events_pb2.Event.EventSeverity.Name(self._proto.severity)
            if name == "WARNING_NEW" or name == "WARNING_OLD":
                # Protobuf serialization format for event severities
                # is going through a migration.
                return "WARNING"
            else:
                return name
        return None

    @property
    def message(self) -> Optional[str]:
        """
        Event message.
        """
        if self._proto.HasField("message"):
            return self._proto.message
        return None

    @property
    def sequence_number(self) -> int:
        """
        Sequence number. Usually this is assigned by the source of the event.
        """
        return self._proto.seqNumber

    @property
    def event_type(self) -> Optional[str]:
        """
        The event type. This is mission-specific and can be any string.
        """
        if self._proto.HasField("type"):
            return self._proto.type
        return None

    @property
    def source(self) -> Optional[str]:
        """
        The event source. Can be any string.
        """
        if self._proto.HasField("source"):
            return self._proto.source
        return None

    @property
    def extra(self) -> Dict[str, str]:
        """
        Dict with extra event properties.

        .. versionadded:: 1.8.4
           Compatible with Yamcs 5.7.3 onwards
        """
        return {key: self._proto.extra[key] for key in self._proto.extra}

    def __str__(self):
        return f"{self.generation_time} [{self.severity}] {self.message}"


class Link:
    """
    Represents a link with an external system. Depending on the
    semantics of the link, this may imply inbound data, outbound
    data or a combination of both.
    """

    def __init__(self, proto):
        self._proto = proto
        self._actions = [LinkAction(action) for action in self._proto.actions]
        self._extra = {key: value for key, value in proto.extra.items()}

    @property
    def instance(self) -> str:
        """Name of the instance where this link is defined."""
        return self._proto.instance

    @property
    def name(self) -> str:
        """Name of this link (unique per instance)."""
        return self._proto.name

    @property
    def class_name(self) -> str:
        """Name of this link's class."""
        return self._proto.type

    @property
    def enabled(self) -> bool:
        """If ``True``, this link accepts or outputs data."""
        return not self._proto.disabled

    @property
    def status(self) -> str:
        """Short status."""
        return self._proto.status

    @property
    def in_count(self) -> int:
        """The number of inbound data events (example: packet count)."""
        return self._proto.dataInCount

    @property
    def out_count(self) -> int:
        """The number of outbound data events (example: command count)."""
        return self._proto.dataOutCount

    @property
    def actions(self) -> List["LinkAction"]:
        """Custom actions."""
        return self._actions

    @property
    def extra(self) -> Dict[str, Any]:
        """Custom info fields."""
        return self._extra

    def __str__(self):
        desc = f"{self.instance}/{self.name}"
        return f"{desc}: {self.status} (in: {self.in_count} out: {self.out_count})"


class LinkAction:
    def __init__(self, proto):
        self._proto = proto

    def __str__(self):
        return str(self._proto)

    @property
    def id(self) -> str:
        """Action ID"""
        return self._proto.id

    @property
    def label(self) -> str:
        """Label for the action"""
        return self._proto.label

    @property
    def style(self) -> str:
        """Action style"""
        return self._proto.style

    @property
    def enabled(self) -> bool:
        """Whether the action is currently enabled"""
        return self._proto.enabled

    @property
    def checked(self) -> bool:
        """Whether the action is currently checked"""
        return self._proto.checked


class RdbTablespace:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Tablespace name"""
        return self._proto.name

    @property
    def data_dir(self) -> str:
        """Data directory"""
        return self._proto.dataDir


class Instance:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Name of this instance."""
        return self._proto.name

    @property
    def state(self) -> str:
        """
        State of this instance. One of ``OFFLINE``, ``INITIALIZING``,
        ``INITIALIZED``, ``STARTING``, ``RUNNING``, ``STOPPING`` or
        ``FAILED``.
        """
        return instances_pb2.YamcsInstance.InstanceState.Name(self._proto.state)

    @property
    def failure_cause(self) -> Optional[str]:
        """Failure message when ``state == 'FAILED'``"""
        if self._proto.HasField("failureCause"):
            return self._proto.failureCause
        return None

    @property
    def mission_time(self) -> Optional[datetime.datetime]:
        """
        Mission time of this instance's time service.
        """
        if self._proto.HasField("missionTime"):
            return parse_server_time(self._proto.missionTime)
        return None

    def __str__(self):
        return f"{self.name} [{self.state}]"


class InstanceTemplate:
    """A template for creating an instance."""

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Name of this template."""
        return self._proto.name

    def __str__(self):
        return self.name


class Service:
    """A Yamcs service."""

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Name of this service."""
        return self._proto.name

    @property
    def instance(self) -> Optional[str]:
        """Name of the instance where this service is defined."""
        if self._proto.HasField("instance"):
            return self._proto.instance
        return None

    @property
    def processor(self) -> Optional[str]:
        """Name of the processor where this service is defined."""
        if self._proto.HasField("processor"):
            return self._proto.processor
        return None

    @property
    def class_name(self) -> str:
        """Name of this service's class."""
        return self._proto.className

    @property
    def state(self) -> str:
        """State of this service."""
        return services_pb2.ServiceState.Name(self._proto.state)

    def failure_message(self) -> Optional[str]:
        """
        Short failure message when state is ``FAILED``

        .. versionadded:: 1.9.0
           Compatible with Yamcs 5.8.0 onwards
        """
        if self._proto.HasField("failureMessage"):
            return self._proto.failureMessage
        return None

    def failure_cause(self) -> Optional[str]:
        """
        Java stacktrace when state is ``FAILED``

        .. versionadded:: 1.9.0
           Compatible with Yamcs 5.8.0 onwards
        """
        if self._proto.HasField("failureCause"):
            return self._proto.failureCause
        return None

    def __str__(self):
        return f"{self.name} [{self.state}]"


class Processor:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Name of this processor."""
        return self._proto.name

    @property
    def instance(self) -> str:
        """Name of the instance where this processor is defined."""
        return self._proto.instance

    @property
    def state(self) -> str:
        """State of this processor."""
        return services_pb2.ServiceState.Name(self._proto.state)

    @property
    def type(self) -> str:
        """Type of this processor."""
        return self._proto.type

    @property
    def owner(self) -> str:
        """User that owns this processor."""
        return self._proto.creator

    @property
    def persistent(self) -> bool:
        """If ``True``, this processor does not close if no clients are connected."""
        return self._proto.persistent

    @property
    def protected(self) -> bool:
        """If ``True``, this processor can not be deleted."""
        return self._proto.protected

    @property
    def mission_time(self) -> Optional[datetime.datetime]:
        """
        Mission time of this processor.
        """
        if self._proto.HasField("time"):
            return parse_server_time(self._proto.time)
        return None

    def __str__(self):
        return f"{self.name} [{self.state}]"


class LoadParameterValuesResult:
    """
    Statistics returned when loading a stream of
    parameter values.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def value_count(self) -> str:
        """Number of loaded parameter values."""
        return self._proto.valueCount

    @property
    def min_generation_time(self) -> Optional[datetime.datetime]:
        """Minimum geneneration time of all loaded parameter values"""
        if self._proto.HasField("minGenerationTime"):
            return parse_server_time(self._proto.minGenerationTime)
        return None

    @property
    def max_generation_time(self) -> Optional[datetime.datetime]:
        """Maximum geneneration time of all loaded parameter values"""
        if self._proto.HasField("maxGenerationTime"):
            return parse_server_time(self._proto.maxGenerationTime)
        return None

    def __str__(self) -> str:
        result = f"{self.value_count} values"
        if self.max_generation_time:
            result += (
                f" in range [{self.min_generation_time} - {self.max_generation_time}]"
            )
        return result


class SdlsStats:
    def __init__(self, proto):
        self._proto = proto

    @property
    def instance(self) -> Optional[str]:
        if self._proto.HasField("instance"):
            return self._proto.instance
        return None

    @property
    def link_name(self) -> Optional[str]:
        if self._proto.HasField("linkName"):
            return self._proto.linkName
        return None

    @property
    def spi(self) -> Optional[int]:
        if self._proto.HasField("spi"):
            return self._proto.spi
        return None

    @property
    def seq(self) -> Optional[int]:
        if self._proto.HasField("seqCtr"):
            return self._proto.seqCtr
        return None
