from datetime import datetime
from typing import Optional
from yamcs.core.helpers import parse_server_time
from yamcs.protobuf.activities import activities_pb2

class ActivityInfo:
    """
    Activity Info
    """
    def __init__(self, proto : activities_pb2.ActivityInfo):
        self._proto = proto

    @property
    def id(self) -> str:
        """
        Activity identifier
        """
        return self._proto.id

    @property
    def start(self) -> datetime:
        """
        Start time of the activity
        """
        return parse_server_time(self._proto.start)

    @property
    def seq(self) -> int:
        """
        Differentiator in case of multiple activities with the same start time
        """
        return self._proto.seq

    @property
    def status(self) -> str:
        """
        Activity status
        """
        return activities_pb2.ActivityStatus.Name(self._proto.status)

    @property
    def startedBy(self) -> str:
        """
        User who started the run
        """
        return self._proto.startedBy

    @property
    def type(self) -> str:
        """
        Activity type
        """
        return self._proto.type

    @property
    def detail(self) -> str:
        """
        Activity detail (short descriptive)
        """
        return self._proto.detail

    @property
    def stopped(self) -> Optional[datetime]:
        """
        Stop time of the activity run
        """
        if self._proto.HasField("stopped"):
            return parse_server_time(self._proto.stopped)
        return None

    @property
    def stoppedBy(self) -> Optional[str]:
        """
        User who stopped the run.
        Only set if the activity was manually stopped
        """
        if self._proto.HasField("stoppedBy"):
            return self._proto.stoppedBy
        return None

    @property
    def failureReason(self) -> Optional[str]:
        """
        If set, the activity is stopped, but failed
        """
        if self._proto.HasField("failureReason"):
            return self._proto.failureReason
        return None

    def __str__(self):
        return f"[{self.id}] {self.start} {self.type}"

class ActivityLogInfo:
    """
    Activity Log Info
    """
    def __init__(self, proto : activities_pb2.ActivityLogInfo):
        self._proto = proto

    @property
    def time(self) -> datetime:
        """
        Log time
        """
        return parse_server_time(self._proto.time)

    @property
    def source(self) -> str:
        """
        Source of this log message. One of:
        - SERVICE: the log is generated by the activity service
        - ACTIVITY: the log is generated by the activity itself
        """
        return self._proto.source

    @property
    def level(self) -> str:
        """
        Log level
        """
        return activities_pb2.ActivityLogLevel.Name(self._proto.level)

    @property
    def message(self) -> str:
        """
        Log level
        """
        return self._proto.message

    def __str__(self):
        return f"{self.time:%Y-%m-%d %H:%M:%S} {self.source:8} {self.level:10} {self.message}"

class ExecutorInfo:
    """
    Executor Info
    """
    def __init__(self, proto : activities_pb2.ExecutorInfo):
        self._proto = proto

    @property
    def type(self) -> str:
        """
        Executor type
        """
        return self._proto.type

    @property
    def displayName(self) -> str:
        """
        Executor display name
        """
        return self._proto.displayName

    @property
    def description(self) -> str:
        """
        Executor description
        """
        return self._proto.description

    @property
    def icon(self) -> str:
        """
        Name of an icon in the Material Icons font.
        """
        return self._proto.icon

    def __str__(self):
        return f"{self.type:13} {self.displayName:13} {self.description}"
