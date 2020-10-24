from yamcs.core.helpers import parse_server_time
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.yamcsManagement import yamcsManagement_pb2


class AuthInfo:
    """
    Authentication information
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def require_authentication(self):
        return self._proto.requireAuthentication


class ServerInfo:
    """
    General server properties.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def id(self):
        """The Server ID."""
        return self._proto.serverId

    @property
    def version(self):
        """The version of Yamcs Server."""
        return self._proto.yamcsVersion

    @property
    def default_yamcs_instance(self):
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
    def username(self):
        return self._proto.name

    @property
    def superuser(self):
        return self._proto.superuser

    @property
    def system_privileges(self):
        return [p for p in self._proto.systemPrivilege]

    @property
    def object_privileges(self):
        return [ObjectPrivilege(p) for p in self._proto.objectPrivilege]

    def __str__(self):
        return self.username


class ObjectPrivilege:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        return self._proto.type

    @property
    def objects(self):
        return [o for o in self._proto.object]

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
    def generation_time(self):
        """
        The time when the event was generated.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("generationTime"):
            return parse_server_time(self._proto.generationTime)
        return None

    @property
    def reception_time(self):
        """
        The time when the event was received by Yamcs.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("receptionTime"):
            return parse_server_time(self._proto.receptionTime)
        return None

    @property
    def severity(self):
        """
        Severity level of the event. One of ``INFO``, ``WATCH``,
        ``WARNING``, ``DISTRESS``, ``CRITICAL`` or ``SEVERE``.
        """
        if self._proto.HasField("severity"):
            return yamcs_pb2.Event.EventSeverity.Name(self._proto.severity)
        return None

    @property
    def message(self):
        """
        Event message.
        """
        if self._proto.HasField("message"):
            return self._proto.message
        return None

    @property
    def sequence_number(self):
        """
        Sequence number. Usually this is assigned by the source of the event.
        """
        if self._proto.HasField("seqNumber"):
            return self._proto.seqNumber
        return None

    @property
    def event_type(self):
        """
        The event type. This is mission-specific and can be any string.
        """
        if self._proto.HasField("type"):
            return self._proto.type
        return None

    @property
    def source(self):
        """
        The event source. Can be any string.
        """
        if self._proto.HasField("source"):
            return self._proto.source
        return None

    def __str__(self):
        return f"{self.generation_time} [{self.severity}] {self.message}"


class LinkEvent:
    """
    Data holder used in link subscriptions.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def event_type(self):
        """
        The type of the event. One of ``REGISTERED``, ``UNREGISTERED``,
        or ``UPDATED``.
        """
        return yamcsManagement_pb2.LinkEvent.Type.Name(self._proto.type)

    @property
    def link(self):
        """
        Link state at the time of this event.

        :type: :class:`.Link`
        """
        return Link(self._proto.linkInfo)

    def __str__(self):
        return f"[{self.event_type}] {self.link}"


class Link:
    """
    Represents a link with an external system. Depending on the
    semantics of the link, this may imply inbound data, outbound
    data or a combination of both.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def instance(self):
        """Name of the instance where this link is defined."""
        return self._proto.instance

    @property
    def name(self):
        """Name of this link (unique per instance)."""
        return self._proto.name

    @property
    def class_name(self):
        """Name of this link's class."""
        return self._proto.type

    @property
    def enabled(self):
        """If ``True``, this link accepts or outputs data."""
        return not self._proto.disabled

    @property
    def status(self):
        """Short status."""
        return self._proto.status

    @property
    def in_count(self):
        """The number of inbound data events (example: packet count)."""
        return self._proto.dataInCount

    @property
    def out_count(self):
        """The number of outbound data events (example: command count)."""
        return self._proto.dataOutCount

    def __str__(self):
        desc = f"{self.instance}/{self.name}"
        return f"{desc}: {self.status} (in: {self.in_count} out: {self.out_count})"


class Instance:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Name of this instance."""
        return self._proto.name

    @property
    def state(self):
        """
        State of this instance. One of ``OFFLINE``, ``INITIALIZING``,
        ``INITIALIZED``, ``STARTING``, ``RUNNING``, ``STOPPING`` or
        ``FAILED``.
        """
        if self._proto.HasField("state"):
            return yamcsManagement_pb2.YamcsInstance.InstanceState.Name(
                self._proto.state
            )
        return None

    @property
    def failure_cause(self):
        """Failure message when ``state == 'FAILED'``"""
        if self._proto.HasField("failureCause"):
            return self._proto.failureCause
        return None

    @property
    def mission_time(self):
        """
        Mission time of this instance's time service.

        :type: :class:`~datetime.datetime`
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
    def name(self):
        """Name of this template."""
        return self._proto.name

    def __str__(self):
        return self.name


class Service:
    """A Yamcs service."""

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Name of this service."""
        return self._proto.name

    @property
    def instance(self):
        """Name of the instance where this service is defined."""
        if self._proto.HasField("instance"):
            return self._proto.instance
        return None

    @property
    def processor(self):
        """Name of the processor where this service is defined."""
        if self._proto.HasField("processor"):
            return self._proto.processor
        return None

    @property
    def class_name(self):
        """Name of this service's class."""
        return self._proto.className

    @property
    def state(self):
        """State of this service."""
        if self._proto.HasField("state"):
            return yamcsManagement_pb2.ServiceState.Name(self._proto.state)
        return None

    def __str__(self):
        return f"{self.name} [{self.state}]"


class Processor:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Name of this processor."""
        return self._proto.name

    @property
    def instance(self):
        """Name of the instance where this processor is defined."""
        return self._proto.instance

    @property
    def state(self):
        """State of this processor."""
        if self._proto.HasField("state"):
            return yamcsManagement_pb2.ServiceState.Name(self._proto.state)
        return None

    @property
    def type(self):
        """Type of this processor."""
        return self._proto.type

    @property
    def owner(self):
        """User that owns this processor."""
        return self._proto.creator

    @property
    def persistent(self):
        """If ``True``, this processor does not close if no clients are connected."""
        return not self._proto.persistent

    @property
    def mission_time(self):
        """
        Mission time of this processor.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("time"):
            return parse_server_time(self._proto.time)
        return None

    def __str__(self):
        return f"{self.name} [{self.state}]"
