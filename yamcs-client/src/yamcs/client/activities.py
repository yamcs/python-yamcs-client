import abc
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional, Union

import pkg_resources
from yamcs.client.core.helpers import to_argument_value
from yamcs.protobuf.activities import activities_pb2

__all__ = [
    "Activity",
    "CommandActivity",
    "CommandStackActivity",
    "ManualActivity",
    "ScriptActivity",
]


@dataclass
class Activity:
    """
    Superclass for activities. Core implementations:

    * :class:`.CommandActivity`
    * :class:`.CommandStackActivity`
    * :class:`.ManualActivity`
    * :class:`.ScriptActivity`
    """

    @staticmethod
    @abc.abstractmethod
    def _from_proto(proto: activities_pb2.ActivityDefinitionInfo) -> "Activity":
        pass

    @abc.abstractmethod
    def _to_proto(self) -> activities_pb2.ActivityDefinitionInfo:
        pass

    @staticmethod
    def _as_subclass(proto):
        # No need for MANUAL.
        # It is recognized by Yamcs, by not having an
        # activity definition.
        if proto.type == "COMMAND":
            return CommandActivity._from_proto(proto)
        elif proto.type == "COMMAND_STACK":
            return CommandStackActivity._from_proto(proto)
        elif proto.type == "SCRIPT":
            return ScriptActivity._from_proto(proto)
        else:
            for entry in pkg_resources.iter_entry_points(
                group="yamcs.client.activities"
            ):
                if proto.type == entry.name:
                    activity_cls = entry.load()
                    return activity_cls._from_proto(proto)

            raise ValueError(f"Unexpected activity type: {proto.type}")


@dataclass
class ManualActivity(Activity):
    """
    An activity whose execution status is managed outside of Yamcs
    """


@dataclass
class ScriptActivity(Activity):
    """
    An activity that runs a script
    """

    script: str
    """
    Script identifier.

    This should be the relative path to an an executable file in one of
    the search locations. When unconfigured, the default search
    location is :file:`etc/scripts/` relative to the Yamcs working
    directory.
    """

    args: Optional[Union[str, List[str]]] = None
    """
    Optional script arguments, passed verbatim in the command line.
    """

    processor: Optional[str] = None
    """
    Optional processor name. If provided, this is provided to the
    script as the environment variable ``YAMCS_PROCESSOR``.
    """

    @staticmethod
    def _from_proto(proto: activities_pb2.ActivityDefinitionInfo):
        activity = ScriptActivity(script=proto.args["script"])

        if "args" in proto.args:
            activity.args = proto.args["args"]

        if "processor" in proto.args:
            activity.processor = proto.args["processor"]

        return activity

    def _to_proto(self) -> activities_pb2.ActivityDefinitionInfo:
        proto = activities_pb2.ActivityDefinitionInfo()
        proto.type = "SCRIPT"
        proto.args["script"] = self.script

        if self.args:
            proto.args["args"] = self.args

        if self.processor:
            proto.args["processor"] = self.processor

        return proto


@dataclass
class CommandActivity(Activity):
    """
    An activity that executes a single command
    """

    command: str
    """Qualified name of a command"""

    args: Mapping[str, Any] = field(default_factory=dict)
    """Named arguments, if the command requires any"""

    extra: Mapping[str, Any] = field(default_factory=dict)
    """Extra command options"""

    processor: Optional[str] = None
    """
    Optional processor name. If not provided, Yamcs defaults to any
    processor it can find with commanding enabled.
    """

    @staticmethod
    def _from_proto(proto: activities_pb2.ActivityDefinitionInfo):
        activity = CommandActivity(command=proto.args["command"])

        if "args" in proto.args:
            command_args = proto.args["args"]
            activity.args = {key: value for key, value in command_args.items()}

        if "extra" in proto.args:
            command_extra = proto.args["extra"]
            activity.extra = {key: value for key, value in command_extra.items()}

        if "processor" in proto.args:
            activity.processor = proto.args["processor"]

        return activity

    def _to_proto(self) -> activities_pb2.ActivityDefinitionInfo:
        proto = activities_pb2.ActivityDefinitionInfo()
        proto.type = "COMMAND"
        proto.args["command"] = self.command

        if self.processor:
            proto.args["processor"] = self.processor

        proto.args["args"] = {}
        for k, v in self.args.items():
            proto.args["args"][k] = to_argument_value(v, force_string=True)

        proto.args["extra"] = {}
        for k, v in self.extra.items():
            proto.args["extra"][k] = to_argument_value(v, force_string=False)

        return proto


@dataclass
class CommandStackActivity(Activity):
    """
    An activity that executes a command stack
    """

    bucket: str
    """The name of the bucket containing the stack."""

    stack: str
    """The name of the stack object inside the bucket."""

    processor: Optional[str] = None
    """
    Optional processor name. If not provided, Yamcs defaults to any
    processor it can find with commanding enabled.
    """

    @staticmethod
    def _from_proto(proto: activities_pb2.ActivityDefinitionInfo):
        activity = CommandStackActivity(
            bucket=proto.args["bucket"],
            stack=proto.args["stack"],
        )

        if "processor" in proto.args:
            activity.processor = proto.args["processor"]

        return activity

    def _to_proto(self) -> activities_pb2.ActivityDefinitionInfo:
        proto = activities_pb2.ActivityDefinitionInfo()
        proto.type = "COMMAND_STACK"
        proto.args["bucket"] = self.bucket
        proto.args["stack"] = self.stack
        if self.processor:
            proto.args["processor"] = self.processor
        return proto
