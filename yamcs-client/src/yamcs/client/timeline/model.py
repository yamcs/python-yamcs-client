import abc
import datetime
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union, cast

from yamcs.client.activities import Activity
from yamcs.client.core.helpers import ProtoList, parse_server_time, to_server_time
from yamcs.protobuf.timeline import timeline_pb2

__all__ = [
    "Band",
    "CommandBand",
    "ItemBand",
    "OnCompletion",
    "OnFailure",
    "OnStart",
    "OnSuccess",
    "ParameterPlot",
    "ParameterStateBand",
    "Predecessor",
    "RangeMapping",
    "Spacer",
    "StartCondition",
    "TimelineActivity",
    "TimelineEvent",
    "TimelineItem",
    "TimelineTask",
    "TimeRuler",
    "Trace",
    "ValueMapping",
    "View",
]


class StartCondition(Enum):
    """
    Defines conditions for starting an activity relative to another item.

    This enum specifies when an activity should start based on the execution
    status of a predecessor item.
    """

    ON_COMPLETION = "ON_COMPLETION"
    """Start the item regardless of the predecessor's outcome."""
    ON_SUCCESS = "ON_SUCCESS"
    """Start the item only if the predecessor completes successfully."""
    ON_FAILURE = "ON_FAILURE"
    """Start the item only if the predecessor fails."""
    ON_START = "ON_START"
    """Start the item as soon as the predecessor starts."""

    def _to_proto(self):
        if self == StartCondition.ON_COMPLETION:
            return timeline_pb2.StartCondition.ON_COMPLETION
        elif self == StartCondition.ON_SUCCESS:
            return timeline_pb2.StartCondition.ON_SUCCESS
        elif self == StartCondition.ON_FAILURE:
            return timeline_pb2.StartCondition.ON_FAILURE
        elif self == StartCondition.ON_START:
            return timeline_pb2.StartCondition.ON_START
        else:
            raise ValueError("Unexpected start condition")

    @staticmethod
    def _from_proto(value):
        if value == timeline_pb2.StartCondition.ON_COMPLETION:
            return StartCondition.ON_COMPLETION
        elif value == timeline_pb2.StartCondition.ON_SUCCESS:
            return StartCondition.ON_SUCCESS
        elif value == timeline_pb2.StartCondition.ON_FAILURE:
            return StartCondition.ON_FAILURE
        elif value == timeline_pb2.StartCondition.ON_START:
            return StartCondition.ON_START
        else:
            raise ValueError("Unexpected start condition")


@dataclass
class OnCompletion:
    """
    The item starts only if the predecessor has completed (either through
    success or failure).
    """

    item: Union["TimelineItem", str]
    """Predecessor item (or its identifier)"""

    @property
    def item_id(self) -> str:
        """Item identifier of the predecessor"""
        if isinstance(self.item, TimelineItem):
            return self.item.id
        else:
            return self.item

    def _to_predecessor(self) -> "Predecessor":
        return Predecessor(self.item, start_condition=StartCondition.ON_COMPLETION)


@dataclass
class OnSuccess:
    """The item starts only if the predecessor has completed successfully."""

    item: Union["TimelineItem", str]
    """Predecessor item (or its identifier)"""

    @property
    def item_id(self) -> str:
        """Item identifier of the predecessor"""
        if isinstance(self.item, TimelineItem):
            return self.item.id
        else:
            return self.item

    def _to_predecessor(self) -> "Predecessor":
        return Predecessor(self.item, start_condition=StartCondition.ON_SUCCESS)


@dataclass
class OnFailure:
    """The item starts only if the predecessor has failed."""

    item: Union["TimelineItem", str]
    """Predecessor item (or its identifier)"""

    @property
    def item_id(self) -> str:
        """Item identifier of the predecessor"""
        if isinstance(self.item, TimelineItem):
            return self.item.id
        else:
            return self.item

    def _to_predecessor(self) -> "Predecessor":
        return Predecessor(self.item, start_condition=StartCondition.ON_FAILURE)


@dataclass
class OnStart:
    """The item starts as soon as the predecessor has started."""

    item: Union["TimelineItem", str]
    """Predecessor item (or its identifier)"""

    @property
    def item_id(self) -> str:
        """Item identifier of the predecessor"""
        if isinstance(self.item, TimelineItem):
            return self.item.id
        else:
            return self.item

    def _to_predecessor(self) -> "Predecessor":
        return Predecessor(self.item, start_condition=StartCondition.ON_START)


StartTrigger = Union[OnSuccess, OnFailure, OnCompletion, OnStart]
"""
Expresses a dependency between an item and its predecessor.
"""


@dataclass
class Predecessor:

    item: Union[str, "TimelineItem"]
    """Predecessor item (or its identifier)"""

    start_condition: StartCondition = StartCondition.ON_SUCCESS
    """The condition required"""

    @property
    def item_id(self) -> str:
        """Item identifier of the predecessor"""
        if isinstance(self.item, TimelineItem):
            return self.item.id
        else:
            return self.item

    @staticmethod
    def _from_proto(proto: timeline_pb2.PredecessorInfo) -> "Predecessor":
        return Predecessor(
            item=proto.itemId,
            start_condition=StartCondition._from_proto(proto.startCondition),
        )

    def _to_proto(self) -> timeline_pb2.PredecessorInfo:
        proto = timeline_pb2.PredecessorInfo()
        proto.itemId = self.item_id
        proto.startCondition = self.start_condition._to_proto()
        return proto


class TimelineItem(abc.ABC):

    def __init__(
        self,
        *,
        name: str,
        start: Union[datetime.datetime, StartTrigger, List[StartTrigger]],
        duration: Optional[datetime.timedelta],
        id: Optional[str],
        tags: Optional[List[str]],
        auto_start: bool,
        extra: Optional[Dict[str, str]],
    ):
        """
        :param name:
            Name of this item
        :param start:
            Item start condition
        :param duration:
            Item duration
        :param id:
            Item identifier. If empty, the client will automatically determine a random
            identifier.
        :param tags:
            Item tags. Used by bands to filter what is visible.
        :param auto_start:
            Whether the activity starts automatically. Else it
            would require a separate API call to start it.
        :param extra:
            Project-specific properties (ignored by Yamcs)
        """

        self.name: str = name
        """Name of this item"""

        self.start: Union[datetime.datetime, StartTrigger, List[StartTrigger]] = start
        """Item start condition"""

        self.duration: datetime.timedelta = duration or datetime.timedelta(seconds=0)
        """Item duration"""

        self.id: str = id or str(uuid.uuid4())
        """Item identifier"""

        self.tags: List[str] = list(tags or [])
        """
        Item tags. Used by bands to filter what is visible.
        """

        self.auto_start: bool = auto_start
        """
        Whether the item starts automatically. Else it
        would require a separate API call to start it.
        """

        self.extra: Dict[str, str] = dict(extra or {})
        """Project-specific properties (ignored by Yamcs)"""

        self._start_time: Optional[datetime.datetime] = None
        """
        Item start time.

        This attribute is derived from the start conditions.
        """

        if isinstance(self.start, datetime.datetime):
            self._start_time = self.start

    @property
    def start_time(self) -> datetime.datetime:
        """
        **Readonly property**

        Returns the start time of this item.

        This may be a time derived by the server based on the item's start conditions.
        """
        if self._start_time:
            return self._start_time
        else:
            raise ValueError("Start time unknown")

    @property
    def predecessors(self) -> List[Predecessor]:
        """
        **Readonly property**

        Returns the predecessors for this item, derived from the item's start
        conditions.
        """
        if isinstance(self.start, StartTrigger):
            return [self.start._to_predecessor()]
        elif isinstance(self.start, list):
            return [x._to_predecessor() for x in self.start]
        else:
            return []

    @staticmethod
    def _to_start_trigger(predecessor: Predecessor) -> StartTrigger:
        if predecessor.start_condition == StartCondition.ON_SUCCESS:
            return OnSuccess(predecessor.item_id)
        elif predecessor.start_condition == StartCondition.ON_FAILURE:
            return OnFailure(predecessor.item_id)
        elif predecessor.start_condition == StartCondition.ON_COMPLETION:
            return OnCompletion(predecessor.item_id)
        elif predecessor.start_condition == StartCondition.ON_START:
            return OnStart(predecessor.item_id)
        else:
            raise ValueError("Unexpected start condition")

    @staticmethod
    @abc.abstractmethod
    def _from_proto(proto: timeline_pb2.TimelineItem) -> "TimelineItem":
        pass

    @staticmethod
    def _as_subclass(proto: timeline_pb2.TimelineItem):
        if proto.type == timeline_pb2.TimelineItemType.ACTIVITY:
            if proto.HasField("activityDefinition"):
                return TimelineActivity._from_proto(proto)
            else:
                return TimelineTask._from_proto(proto)
        elif proto.type == timeline_pb2.TimelineItemType.EVENT:
            return TimelineEvent._from_proto(proto)
        else:
            raise ValueError("Unexpected item type")

    def _to_proto(self) -> timeline_pb2.TimelineItem:
        proto = timeline_pb2.TimelineItem()
        proto.id = self.id
        proto.name = self.name
        proto.autoStart = self.auto_start
        proto.duration.FromTimedelta(self.duration)
        proto.tags[:] = self.tags
        proto.predecessors.extend([x._to_proto() for x in self.predecessors])

        if isinstance(self.start, datetime.datetime):
            proto.start.MergeFrom(to_server_time(self.start))

        for k, v in self.extra.items():
            proto.extra[k] = v

        return proto


class TimelineEvent(TimelineItem):
    """
    An event on the timeline. This has a fixed start time, and an
    optional duration.

    Events are used to show any kind of information on the timeline,
    and can serve as an anchor point for depending activities.
    """

    def __init__(
        self,
        name: str,
        *,
        start: datetime.datetime,
        id: Optional[str] = None,
        duration: Optional[datetime.timedelta] = None,
        tags: Optional[List[str]] = None,
        background_color: Optional[str] = None,
        border_color: Optional[str] = None,
        border_width: Optional[int] = None,
        corner_radius: Optional[int] = None,
        margin_left: Optional[int] = None,
        text_color: Optional[str] = None,
        text_size: Optional[int] = None,
        extra: Optional[Dict[str, str]] = None,
    ):
        """
        :param name:
            Event title
        :param start:
            Event start
        :param duration:
            Event duration. If emtpy, the event is considered to be a *milestone*.
        :param id:
            Item identifier. If empty, the client will automatically determine a random
            identifier.
        :param tags:
            Item tags. Used by bands to filter what is visible.
        :param background_color:
            Box background color (CSS color string)
        :param border_color:
            Box border color (CSS color string)
        :param border_width:
            Thickness of box border
        :param corner_radius:
            Radius of box corners
        :param margin_left:
            Distance between box start and label
        :param text_color:
            Text color (CSS color string)
        :param text_size:
            Text size
        :param extra:
            Project-specific properties (ignored by Yamcs)
        """
        TimelineItem.__init__(
            self,
            name=name,
            start=start,
            id=id,
            duration=duration,
            tags=tags,
            auto_start=True,
            extra=extra,
        )
        self.background_color: Optional[str] = background_color
        """Box background color (CSS color string)"""
        self.border_color: Optional[str] = border_color
        """Box border color (CSS color string)"""
        self.border_width: Optional[int] = border_width
        """Thickness of box border"""
        self.corner_radius: Optional[int] = corner_radius
        """Radius of box corners"""
        self.margin_left: Optional[int] = margin_left
        """Distance between box start and label"""
        self.text_color: Optional[str] = text_color
        """Text color (CSS color string)"""
        self.text_size: Optional[int] = text_size
        """Text size"""

    def _to_proto(self) -> timeline_pb2.TimelineItem:
        proto = super()._to_proto()
        proto.type = timeline_pb2.TimelineItemType.EVENT

        if self.background_color:
            proto.properties["backgroundColor"] = self.background_color
        if self.border_color:
            proto.properties["borderColor"] = self.border_color
        if self.border_width is not None:
            proto.properties["borderWidth"] = str(self.border_width)
        if self.corner_radius is not None:
            proto.properties["cornerRadius"] = str(self.corner_radius)
        if self.margin_left is not None:
            proto.properties["marginLeft"] = str(self.margin_left)
        if self.text_color:
            proto.properties["textColor"] = self.text_color
        if self.text_size is not None:
            proto.properties["textSize"] = str(self.text_size)

        return proto

    @staticmethod
    def _from_proto(proto: timeline_pb2.TimelineItem) -> "TimelineEvent":
        item = TimelineEvent(
            id=proto.id,
            name=proto.name,
            start=parse_server_time(proto.start),
            duration=proto.duration.ToTimedelta(),
            tags=proto.tags,
        )

        for k, v in proto.extra.items():
            item.extra[k] = v

        if "backgroundColor" in proto.properties:
            item.background_color = proto.properties["backgroundColor"]
        if "borderColor" in proto.properties:
            item.border_color = proto.properties["borderColor"]
        if "borderWidth" in proto.properties:
            item.border_width = int(proto.properties["borderWidth"])
        if "cornerRadius" in proto.properties:
            item.corner_radius = int(proto.properties["cornerRadius"])
        if "marginLeft" in proto.properties:
            item.margin_left = int(proto.properties["marginLeft"])
        if "textColor" in proto.properties:
            item.text_color = proto.properties["textColor"]
        if "textSize" in proto.properties:
            item.text_size = int(proto.properties["textSize"])

        return item


@dataclass
class TimelineActivity(TimelineItem):
    """
    An activity on the timeline. Activities can be scheduled at a fixed
    time, or they can be scheduled relative to predecessor items.

    Activities can be assigned an expected duration, which helps
    following ongoing tasks in the Yamcs Web UI.

    Activities can be anything ranging from issuing a single command,
    to running a lengthy script.
    """

    def __init__(
        self,
        name: str,
        *,
        start: Union[datetime.datetime, StartTrigger, List[StartTrigger]],
        duration: Optional[datetime.timedelta] = None,
        id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        auto_start: bool = True,
        activity: Activity,
        extra: Optional[Dict[str, str]] = None,
    ):
        """
        :param name:
            Name of this activity
        :param start:
            Activity start condition
        :param duration:
            Expected activity duration
        :param id:
            Activity identifier. If empty, the client will automatically
            determine a random identifier.
        :param tags:
            Activity tags. Used by bands to filter what is visible.
        :param auto_start:
            Whether the activity starts automatically. Else it
            would require a separate API call to start it.
        :param activity:
            Activity definition
        :param extra:
            Project-specific properties (ignored by Yamcs)
        """
        TimelineItem.__init__(
            self,
            name=name,
            start=start,
            duration=duration,
            id=id,
            tags=tags,
            auto_start=auto_start,
            extra=extra,
        )

        self.activity = activity
        """Activity definition"""

    @staticmethod
    def _from_proto(proto: timeline_pb2.TimelineItem) -> "TimelineActivity":
        predecessors = cast(
            List[Predecessor],
            ProtoList(proto, "predecessors", lambda x: Predecessor._from_proto(x)),
        )
        if not predecessors:
            start = parse_server_time(proto.start)
        elif len(predecessors) == 1:
            start = TimelineItem._to_start_trigger(predecessors[0])
        else:
            start = [TimelineItem._to_start_trigger(x) for x in predecessors]

        item = TimelineActivity(
            id=proto.id,
            name=proto.name,
            start=start,
            duration=proto.duration.ToTimedelta(),
            tags=proto.tags,
            activity=Activity._as_subclass(proto.activityDefinition),
        )

        # Server-derived start time
        if proto.HasField("start"):
            item._start_time = parse_server_time(proto.start)

        for k, v in proto.extra.items():
            item.extra[k] = v

        return item

    def _to_proto(self) -> timeline_pb2.TimelineItem:
        proto = super()._to_proto()
        proto.type = timeline_pb2.TimelineItemType.ACTIVITY
        if self.activity:
            proto.activityDefinition.MergeFrom(self.activity._to_proto())
        else:
            raise ValueError("Missing activity definition")
        return proto


@dataclass
class TimelineTask(TimelineItem):
    """
    A task on the timeline. Tasks are actions to be performed by the
    user. Tasks can be scheduled at a fixed time, or they can be
    scheduled relative to predecessor items.

    Tasks can be assigned an expected duration, which helps
    following ongoing tasks in the Yamcs Web UI.
    """

    def __init__(
        self,
        name: str,
        *,
        start: Union[datetime.datetime, StartTrigger, List[StartTrigger]],
        duration: Optional[datetime.timedelta] = None,
        id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        auto_start: bool = False,
        extra: Optional[Dict[str, str]] = None,
    ):
        """
        :param name:
            Name of this task
        :param start:
            Task start condition
        :param duration:
            Expected task duration
        :param id:
            Task identifier. If empty, the client will automatically
            determine a random identifier.
        :param tags:
            Task tags. Used by bands to filter what is visible.
        :param auto_start:
            Whether the task starts automatically. Else it
            would require a separate API call to start it.

            Tasks have auto_start disabled by default, so that the user
            must indicate both when the task has started, and when it
            has completed.
        :param extra:
            Project-specific properties (ignored by Yamcs)
        """
        TimelineItem.__init__(
            self,
            name=name,
            start=start,
            duration=duration,
            id=id,
            tags=tags,
            auto_start=auto_start,
            extra=extra,
        )

    @staticmethod
    def _from_proto(proto: timeline_pb2.TimelineItem) -> "TimelineTask":
        predecessors = cast(
            List[Predecessor],
            ProtoList(proto, "predecessors", lambda x: Predecessor._from_proto(x)),
        )
        if not predecessors:
            start = parse_server_time(proto.start)
        elif len(predecessors) == 1:
            start = TimelineItem._to_start_trigger(predecessors[0])
        else:
            start = [TimelineItem._to_start_trigger(x) for x in predecessors]

        item = TimelineTask(
            id=proto.id,
            name=proto.name,
            start=start,
            duration=proto.duration.ToTimedelta(),
            tags=proto.tags,
        )

        # Server-derived start time
        if proto.HasField("start"):
            item._start_time = parse_server_time(proto.start)

        for k, v in proto.extra.items():
            item.extra[k] = v

        return item

    def _to_proto(self) -> timeline_pb2.TimelineItem:
        proto = super()._to_proto()
        proto.type = timeline_pb2.TimelineItemType.ACTIVITY
        return proto


class Band(abc.ABC):
    """
    Superclass for bands. Implementations:

    * :class:`.TimeRuler`
    * :class:`.ItemBand`
    * :class:`.ParameterPlot`
    * :class:`.ParameterStateBand`
    * :class:`.Spacer`
    * :class:`.CommandBand`
    """

    def __init__(self, proto):
        self._proto = proto

        if not self._proto.id:
            self._proto.id = str(uuid.uuid4())

    @property
    def id(self) -> str:
        """Band identifier."""
        return self._proto.id

    @id.setter
    def id(self, value: str):
        self._proto.id = value

    @property
    def band_type(self) -> str:
        """Type of band."""
        return timeline_pb2.TimelineBandType.Name(self._proto.type)

    @property
    def name(self) -> str:
        """Name of this band."""
        return self._proto.name

    @name.setter
    def name(self, value: str):
        self._proto.name = value

    @property
    def description(self) -> str:
        """Description of this band."""
        return self._proto.description

    @description.setter
    def description(self, value: str):
        self._proto.description = value

    @property
    def extra(self) -> Dict[str, str]:
        result: Dict[str, Any] = {}
        for k, v in self._proto.extra.items():
            result[k] = v
        return result

    @extra.setter
    def extra(self, value: Dict[str, str]):
        self._proto.extra.clear()
        for k, v in value.items():
            self._proto.extra[k] = v

    def _set_integer_property(self, key: str, value: int):
        if not isinstance(value, int):
            raise ValueError("Provided value is not integer")
        self._proto.properties[key] = str(value)

    def _get_integer_property(self, key: str):
        return int(self._proto.properties[key])

    def _set_optional_float_property(self, key: str, value: Optional[float]):
        if value is None:
            del self._proto.properties[key]
        else:
            if not isinstance(value, (int, float)):
                raise ValueError("Provided value is not float")
            self._proto.properties[key] = str(value)

    def _get_optional_float_property(self, key: Optional[str]) -> Optional[float]:
        return (
            float(self._proto.properties[key])
            if key in self._proto.properties
            else None
        )

    def _set_float_property(self, key: str, value: float):
        if not isinstance(value, (int, float)):
            raise ValueError("Provided value is not float")
        self._proto.properties[key] = str(value)

    def _get_float_property(self, key: str):
        return float(self._proto.properties[key])

    def _set_boolean_property(self, key: str, value: bool):
        if not isinstance(value, bool):
            raise ValueError("Provided value is not boolean")
        self._proto.properties[key] = "true" if value else "false"

    def _get_boolean_property(self, key: str):
        return self._proto.properties[key] == "true"

    def _as_properties(self) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}
        for k, v in self._proto.properties.items():
            properties[k] = v
        return properties

    @staticmethod
    def _as_subclass(proto):
        if proto.type == timeline_pb2.TimelineBandType.TIME_RULER:
            return TimeRuler(proto)
        elif proto.type == timeline_pb2.TimelineBandType.ITEM_BAND:
            return ItemBand(proto)
        elif proto.type == timeline_pb2.TimelineBandType.SPACER:
            return Spacer(proto)
        elif proto.type == timeline_pb2.TimelineBandType.COMMAND_BAND:
            return CommandBand(proto)
        elif proto.type == timeline_pb2.TimelineBandType.PARAMETER_PLOT:
            return ParameterPlot(proto)
        elif proto.type == timeline_pb2.TimelineBandType.PARAMETER_STATES:
            return ParameterStateBand(proto)
        else:
            raise ValueError("Unexpected band type")

    def __str__(self):
        return self.name


class TimeRuler(Band):
    """
    Displays absolute time, formatted in a timezone of choice.
    """

    def __init__(self, proto=None):
        merged = timeline_pb2.TimelineBand()
        merged.type = timeline_pb2.TimelineBandType.TIME_RULER
        merged.properties["timezone"] = "UTC"
        if proto:
            merged.MergeFrom(proto)
        super(TimeRuler, self).__init__(merged)

    @property
    def timezone(self) -> str:
        """
        IANA timezone name.

        Corresponds with the third column of the following table:
        https://data.iana.org/time-zones/data/zone1970.tab

        In addition, the name `UTC` is supported.
        """
        return self._proto.properties["timezone"]

    @timezone.setter
    def timezone(self, value: str):
        self._proto.properties["timezone"] = value


class Spacer(Band):
    """
    Insert empty vertical space.
    """

    def __init__(self, proto=None):
        merged = timeline_pb2.TimelineBand()
        merged.type = timeline_pb2.TimelineBandType.SPACER
        merged.properties["height"] = "34"
        if proto:
            merged.MergeFrom(proto)
        super(Spacer, self).__init__(merged)

    @property
    def height(self) -> int:
        """Spacer height"""
        return self._get_integer_property("height")

    @height.setter
    def height(self, value: int):
        self._set_integer_property("height", value)


class CommandBand(Band):
    """
    Display issued commands.
    """

    def __init__(self, proto=None):
        merged = timeline_pb2.TimelineBand()
        merged.type = timeline_pb2.TimelineBandType.COMMAND_BAND
        if proto:
            merged.MergeFrom(proto)
        super(CommandBand, self).__init__(merged)


@dataclass
class Trace:
    """
    A trace on a :class:`.ParameterPlot`.
    """

    parameter: str
    line_color: str
    visible: bool = True
    line_width: int = 1
    fill: bool = False
    fill_color: str = "#dddddd"
    min_max: bool = False
    min_max_opacity: float = 0.17


class ParameterPlot(Band):
    """
    Plot the values of a numeric parameter.

    .. versionadded:: 1.11.2
       Compatible with Yamcs 5.11.2 onwards
    """

    def __init__(self, proto=None):
        merged = timeline_pb2.TimelineBand()
        merged.type = timeline_pb2.TimelineBandType.PARAMETER_PLOT
        merged.properties["frozen"] = "false"
        merged.properties["height"] = "30"
        merged.properties["zeroLineWidth"] = "0"
        merged.properties["zeroLineColor"] = "#ff0000"
        merged.properties["minimumFractionDigits"] = "0"
        merged.properties["maximumFractionDigits"] = "2"

        self.traces: List[Trace] = []
        """
        Plot lines.
        """

        if proto:
            merged.MergeFrom(proto)

            idx = 1
            while True:
                if f"trace_{idx}_type" in merged.properties:
                    prefix = f"trace_{idx}_"
                    trace = Trace(
                        parameter=merged.properties.get(f"{prefix}parameter"),
                        line_color=merged.properties.get(f"{prefix}lineColor"),
                        visible=bool(merged.properties.get(f"{prefix}visible")),
                        line_width=int(merged.properties.get(f"{prefix}lineWidth")),
                        fill=bool(merged.properties.get(f"{prefix}fill")),
                        fill_color=merged.properties.get(f"{prefix}fillColor"),
                        min_max=bool(merged.properties.get(f"{prefix}minMax")),
                        min_max_opacity=float(
                            merged.properties.get(f"{prefix}minMaxOpacity")
                        ),
                    )
                    self.traces.append(trace)
                    idx += 1
                else:
                    break

        super(ParameterPlot, self).__init__(merged)

    @property
    def frozen(self) -> bool:
        """
        Fix this line to the top of the view. Frozen bands are always
        rendered above other bands.
        """
        return self._get_boolean_property("frozen")

    @frozen.setter
    def frozen(self, value: bool):
        self._set_boolean_property("frozen", value)

    @property
    def height(self) -> int:
        """Band height"""
        return self._get_integer_property("height")

    @height.setter
    def height(self, value: int):
        self._set_integer_property("height", value)

    @property
    def minimum(self) -> Optional[float]:
        """Minimum value to show on Y-axis. Set to ``None`` for fitting actual data"""
        return self._get_optional_float_property("minimum")

    @minimum.setter
    def minimum(self, value: Optional[float]):
        self._set_optional_float_property("minimum", value)

    @property
    def maximum(self) -> Optional[float]:
        """Maximum value to show on Y-axis. Set to ``None`` for fitting actual data"""
        return self._get_optional_float_property("maximum")

    @maximum.setter
    def maximum(self, value: Optional[float]):
        self._set_optional_float_property("maximum", value)

    @property
    def zero_line_width(self) -> int:
        """Thickness of the zero line. 0 is invisible"""
        return self._get_integer_property("zeroLineWidth")

    @zero_line_width.setter
    def zero_line_width(self, value: int):
        self._set_integer_property("zeroLineWidth", value)

    @property
    def zero_line_color(self) -> str:
        """Color of the zero line"""
        return self._proto.properties["zeroLineColor"]

    @zero_line_color.setter
    def zero_line_color(self, value: str):
        self._proto.properties["zeroLineColor"] = value

    @property
    def minimum_fraction_digits(self) -> int:
        """Minimum fraction digits"""
        return self._get_integer_property("minimumFractionDigits")

    @minimum_fraction_digits.setter
    def minimum_fraction_digits(self, value: int):
        self._set_integer_property("minimumFractionDigits", value)

    @property
    def maximum_fraction_digits(self) -> int:
        """Maximum fraction digits"""
        return self._get_integer_property("maximumFractionDigits")

    @maximum_fraction_digits.setter
    def maximum_fraction_digits(self, value: int):
        self._set_integer_property("maximumFractionDigits", value)

    def _as_properties(self) -> Dict[str, Any]:
        props = super(ParameterPlot, self)._as_properties()
        for index, trace in enumerate(self.traces):
            props[f"trace_{index + 1}_parameter"] = trace.parameter
            props[f"trace_{index + 1}_lineColor"] = trace.line_color
            props[f"trace_{index + 1}_visible"] = "true" if trace.visible else "false"
            props[f"trace_{index + 1}_lineWidth"] = str(trace.line_width)
            props[f"trace_{index + 1}_fill"] = "true" if trace.fill else "false"
            props[f"trace_{index + 1}_fillColor"] = trace.fill_color
            props[f"trace_{index + 1}_minMax"] = "true" if trace.min_max else "false"
            props[f"trace_{index + 1}_minMaxOpacity"] = str(trace.min_max_opacity)
        return props


@dataclass
class ValueMapping:
    """
    Maps a value to a label and/or color
    """

    value: Any
    """
    Engineering value to match
    """

    label: Optional[str] = None
    """
    If specified, map the provided value to this label
    """

    color: Optional[str] = None
    """
    If specified, show states of this value (or mapped label) in this color
    """


@dataclass
class RangeMapping:
    """
    Maps a value to a label and/or color.
    """

    start: float
    """
    Match engineering value greater or equal than the provided start value
    """

    end: float
    """
    Match engineering value lesser or equal than the provided end value
    """

    label: Optional[str] = None
    """
    If specified, map the provided value to this label
    """

    color: Optional[str] = None
    """
    If specified, show states of this value (or mapped label) in this color
    """


class ParameterStateBand(Band):
    """
    Show state transitions of a parameter

    .. versionadded:: 1.11.2
       Compatible with Yamcs 5.11.2 onwards
    """

    def __init__(self, proto=None):
        merged = timeline_pb2.TimelineBand()
        merged.type = timeline_pb2.TimelineBandType.PARAMETER_STATES
        merged.properties["frozen"] = "false"
        merged.properties["height"] = "30"
        merged.properties["parameter"] = ""

        self.mappings: List[Union[ValueMapping, RangeMapping]] = []
        """
        Map engineering values to a label and/or color. Mappings are applied
        in order.
        """

        if proto:
            merged.MergeFrom(proto)

            idx = 0
            while True:
                if f"value_mapping_{idx}_type" in merged.properties:
                    prefix = f"value_mapping_{idx}_"
                    type_ = merged.properties[f"{prefix}type"]
                    if type_ == "value":
                        mapping = ValueMapping(
                            value=merged.properties.get(f"{prefix}value"),
                            label=merged.properties.get(f"{prefix}label"),
                            color=merged.properties.get(f"{prefix}color"),
                        )
                        self.mappings.append(mapping)
                    elif type_ == "range":
                        mapping = RangeMapping(
                            start=float(merged.properties.get(f"{prefix}start")),
                            end=float(merged.properties.get(f"{prefix}end")),
                            label=merged.properties.get(f"{prefix}label"),
                            color=merged.properties.get(f"{prefix}color"),
                        )
                        self.mappings.append(mapping)
                    else:
                        raise ValueError(f"Unexpected mapping type '{type_}'")
                    idx += 1
                else:
                    break

        super(ParameterStateBand, self).__init__(merged)

    @property
    def frozen(self) -> bool:
        """
        Fix this line to the top of the view. Frozen bands are always
        rendered above other bands.
        """
        return self._get_boolean_property("frozen")

    @frozen.setter
    def frozen(self, value: bool):
        self._set_boolean_property("frozen", value)

    @property
    def height(self) -> int:
        """Band height"""
        return self._get_integer_property("height")

    @height.setter
    def height(self, value: int):
        self._set_integer_property("height", value)

    @property
    def parameter(self) -> str:
        """Qualified parameter name"""
        return self._proto.properties["parameter"]

    @parameter.setter
    def parameter(self, value: str):
        self._proto.properties["parameter"] = value

    def _as_properties(self) -> Dict[str, Any]:
        props = super(ParameterStateBand, self)._as_properties()
        for index, mapping in enumerate(self.mappings):
            if isinstance(mapping, ValueMapping):
                props[f"value_mapping_{index}_type"] = "value"
                props[f"value_mapping_{index}_value"] = str(mapping.value)
                if mapping.label is not None:
                    props[f"value_mapping_{index}_label"] = str(mapping.label)
                if mapping.color is not None:
                    props[f"value_mapping_{index}_color"] = str(mapping.color)
            elif isinstance(mapping, RangeMapping):
                props[f"value_mapping_{index}_type"] = "range"
                props[f"value_mapping_{index}_start"] = str(mapping.start)
                props[f"value_mapping_{index}_end"] = str(mapping.end)
                if mapping.label is not None:
                    props[f"value_mapping_{index}_label"] = str(mapping.label)
                if mapping.color is not None:
                    props[f"value_mapping_{index}_color"] = str(mapping.color)
        return props


class ItemBand(Band):
    """
    Show a selection of timeline items.
    """

    def __init__(self, proto=None):
        merged = timeline_pb2.TimelineBand()
        merged.type = timeline_pb2.TimelineBandType.ITEM_BAND
        merged.properties["frozen"] = "false"
        merged.properties["itemBackgroundColor"] = "#77b1e1"
        merged.properties["itemBorderColor"] = "#3d94c7"
        merged.properties["itemBorderWidth"] = "1"
        merged.properties["itemCornerRadius"] = "0"
        merged.properties["itemHeight"] = "20"
        merged.properties["itemMarginLeft"] = "5"
        merged.properties["itemTextColor"] = "#333333"
        merged.properties["itemTextOverflow"] = "show"
        merged.properties["itemTextSize"] = "10"
        merged.properties["marginTop"] = "7"
        merged.properties["marginBottom"] = "7"
        merged.properties["multiline"] = "true"
        merged.properties["spaceBetweenItems"] = "7"
        merged.properties["spaceBetweenLines"] = "7"
        if proto:
            merged.MergeFrom(proto)
        super(ItemBand, self).__init__(merged)

    @property
    def frozen(self) -> bool:
        """
        Fix this line to the top of the view. Frozen bands are always
        rendered above other bands.
        """
        return self._get_boolean_property("frozen")

    @frozen.setter
    def frozen(self, value: bool):
        self._set_boolean_property("frozen", value)

    @property
    def tags(self) -> List[str]:
        """
        Item tags that this band filters on.
        """
        return self._proto.tags

    @tags.setter
    def tags(self, value: List[str]):
        self._proto.tags[:] = value

    @property
    def item_background_color(self) -> str:
        """CSS color string."""
        return self._proto.properties["itemBackgroundColor"]

    @item_background_color.setter
    def item_background_color(self, value: str):
        self._proto.properties["itemBackgroundColor"] = value

    @property
    def item_border_color(self) -> str:
        """CSS color string."""
        return self._proto.properties["itemBorderColor"]

    @item_border_color.setter
    def item_border_color(self, value: str):
        self._proto.properties["itemBorderColor"] = value

    @property
    def item_border_width(self) -> int:
        return self._get_integer_property("itemBorderWidth")

    @item_border_width.setter
    def item_border_width(self, value: int):
        self._set_integer_property("itemBorderWidth", value)

    @property
    def item_corner_radius(self) -> int:
        return self._get_integer_property("itemCornerRadius")

    @item_corner_radius.setter
    def item_corner_radius(self, value: int):
        self._set_integer_property("itemCornerRadius", value)

    @property
    def item_height(self) -> int:
        return self._get_integer_property("itemHeight")

    @item_height.setter
    def item_height(self, value: int):
        self._set_integer_property("itemHeight", value)

    @property
    def item_margin_left(self) -> int:
        return self._get_integer_property("itemMarginLeft")

    @item_margin_left.setter
    def item_margin_left(self, value: int):
        self._set_integer_property("itemMarginLeft", value)

    @property
    def item_text_color(self) -> str:
        """CSS color string."""
        return self._proto.properties["itemTextColor"]

    @item_text_color.setter
    def item_text_color(self, value: str):
        self._proto.properties["itemTextColor"] = value

    @property
    def item_text_overflow(self) -> str:
        """One of ``show``, ``clip``, or ``hide``."""
        return self._proto.properties["itemTextOverflow"]

    @item_text_overflow.setter
    def item_text_overflow(self, value: str):
        self._proto.properties["itemTextOverflow"] = value

    @property
    def item_text_size(self) -> int:
        return self._get_integer_property("itemTextSize")

    @item_text_size.setter
    def item_text_size(self, value: int):
        self._set_integer_property("itemTextSize", value)

    @property
    def margin_bottom(self) -> int:
        return self._get_integer_property("marginBottom")

    @margin_bottom.setter
    def margin_bottom(self, value: int):
        self._set_integer_property("marginBottom", value)

    @property
    def margin_top(self) -> int:
        return self._get_integer_property("marginTop")

    @margin_top.setter
    def margin_top(self, value: int):
        self._set_integer_property("marginTop", value)

    @property
    def multiline(self) -> bool:
        """
        Draw items on multiple lines if otherwise there would be collisions.
        """
        return self._get_boolean_property("multiline")

    @multiline.setter
    def multiline(self, value: bool):
        self._set_boolean_property("multiline", value)

    @property
    def space_between_items(self) -> int:
        """
        In case of multilining, this indicates the minimum horizontal space
        between items. If an item does not meet this treshold, it gets
        rendered on a different line.
        """
        return self._get_integer_property("spaceBetweenItems")

    @space_between_items.setter
    def space_between_items(self, value: int):
        self._set_integer_property("spaceBetweenItems", value)

    @property
    def space_between_lines(self) -> int:
        """
        In case of multilining, this indicates the vertical space between
        lines.
        """
        return self._get_integer_property("spaceBetweenLines")

    @space_between_lines.setter
    def space_between_lines(self, value: int):
        self._set_integer_property("spaceBetweenLines", value)


class View:
    def __init__(self, proto=None):
        merged = timeline_pb2.TimelineView()
        if proto:
            merged.MergeFrom(proto)
        self._proto = merged

        if not self._proto.id:
            self._proto.id = str(uuid.uuid4())

        self._bands = ProtoList(self._proto, "bands", lambda x: Band._as_subclass(x))

    @property
    def id(self) -> str:
        """View identifier."""
        return self._proto.id

    @id.setter
    def id(self, value: str):
        self._proto.id = value

    @property
    def name(self) -> str:
        """Name of this view."""
        return self._proto.name

    @name.setter
    def name(self, value: str):
        self._proto.name = value

    @property
    def description(self) -> str:
        """Description of this view."""
        return self._proto.description

    @description.setter
    def description(self, value: str):
        self._proto.name = value

    @property
    def bands(self) -> List[Band]:
        """
        Bands included in this view.
        """
        return self._bands

    @bands.setter
    def bands(self, value: List[Band]):
        self._bands.clear()
        self._bands.extend(value)

    def __str__(self):
        return self.name
