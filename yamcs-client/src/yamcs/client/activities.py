from dataclasses import KW_ONLY, dataclass, field
from typing import Any, List, Mapping, Optional, Union

from yamcs.core.helpers import to_argument_value
from yamcs.protobuf.activities import activities_pb2


@dataclass
class Activity:
    """
    Superclass for activities. Implementations:

    * :class:`.CommandActivity`
    * :class:`.CommandStackActivity`
    * :class:`.ManualActivity`
    * :class:`.ScriptActivity`
    """

    _: KW_ONLY
    comment: Optional[str] = None

    def _from_proto(self, proto: activities_pb2.ActivityDefinitionInfo):
        if proto.HasField("comment"):
            self.comment = proto.comment

        return self

    def _to_proto(self) -> activities_pb2.ActivityDefinitionInfo:
        proto = activities_pb2.ActivityDefinitionInfo()

        if self.comment:
            proto.comment = self.comment

        return proto

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
            raise ValueError("Unexpected activity type")


@dataclass
class ManualActivity(Activity):
    """
    An activity whose execution status is managed outside of Yamcs
    """

    name: str
    """
    Name of the manual activity
    """

    @staticmethod
    def _from_proto(proto: activities_pb2.ActivityDefinitionInfo):
        activity = ManualActivity(name=proto.args["name"])

        return super(ManualActivity, activity)._from_proto(proto)

    def _to_proto(self) -> activities_pb2.ActivityDefinitionInfo:
        proto = super(ManualActivity, self)._to_proto()
        proto.type = "MANUAL"
        proto.args["name"] = self.name
        return proto


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

        return super(ScriptActivity, activity)._from_proto(proto)

    def _to_proto(self) -> activities_pb2.ActivityDefinitionInfo:
        proto = super(ScriptActivity, self)._to_proto()
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

        return super(CommandActivity, activity)._from_proto(proto)

    def _to_proto(self) -> activities_pb2.ActivityDefinitionInfo:
        proto = super(CommandActivity, self)._to_proto()
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

        return super(CommandStackActivity, activity)._from_proto(proto)

    def _to_proto(self) -> activities_pb2.ActivityDefinitionInfo:
        proto = super(CommandStackActivity, self)._to_proto()
        proto.type = "COMMAND_STACK"
        proto.args["bucket"] = self.bucket
        proto.args["stack"] = self.stack
        if self.processor:
            proto.args["processor"] = self.processor
        return proto
