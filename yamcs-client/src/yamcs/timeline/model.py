import abc
from xmlrpc.client import boolean

from yamcs.core.helpers import ProtoList, parse_server_time, to_server_time
from yamcs.protobuf.timeline import timeline_pb2


class View:
    def __init__(self, proto=None):
        merged = timeline_pb2.TimelineView()
        if proto:
            merged.MergeFrom(proto)
        self._proto = merged

        self._bands = ProtoList(self._proto, "bands", lambda x: Band._as_subclass(x))

    @property
    def id(self):
        """View identifier."""
        if self._proto.HasField("id"):
            return self._proto.id
        return None

    @property
    def name(self):
        """Name of this view."""
        return self._proto.name

    @name.setter
    def name(self, value):
        self._proto.name = value

    @property
    def description(self):
        """Description of this view."""
        return self._proto.description

    @description.setter
    def description(self, value):
        self._proto.name = value

    @property
    def bands(self):
        """
        Bands included in this view.

        :type: List[:class:`.Band`]
        """
        return self._bands

    @bands.setter
    def bands(self, value):
        self._bands.clear()
        self._bands.extend(value)

    def __str__(self):
        return self.name


class Item:
    def __init__(self, proto=None):
        merged = timeline_pb2.TimelineItem()
        merged.type = timeline_pb2.TimelineItemType.EVENT
        if proto:
            merged.MergeFrom(proto)
        self._proto = merged

    @property
    def id(self):
        """Item identifier."""
        if self._proto.HasField("id"):
            return self._proto.id
        return None

    @property
    def item_type(self):
        """Type of item."""
        return timeline_pb2.TimelineItemType.Name(self._proto.type)

    @property
    def name(self):
        """Name of this item."""
        return self._proto.name

    @name.setter
    def name(self, value):
        self._proto.name = value

    @property
    def tags(self):
        """
        Item tags. Used by bands to filter what is visible.

        :type: str[]
        """
        return self._proto.tags

    @tags.setter
    def tags(self, value):
        self._proto.tags[:] = value

    @property
    def start(self):
        """
        Item start time.

        :type: :class:`~datetime.datetime`
        """
        if self._proto.HasField("start"):
            return parse_server_time(self._proto.start)
        return None

    @start.setter
    def start(self, value):
        self._proto.start.MergeFrom(to_server_time(value))

    @property
    def duration(self):
        """
        Item duration.

        :type: :class:`~datetime.timedelta`
        """
        if self._proto.HasField("duration"):
            return self._proto.duration.ToTimedelta()
        return None

    @duration.setter
    def duration(self, value):
        self._proto.duration.FromTimedelta(value)

    def __str__(self):
        return self.name


class Band(abc.ABC):
    """
    Superclass for bands. Implementations:

    * :class:`.TimeRuler`
    * :class:`.ItemBand`
    * :class:`.Spacer`
    * :class:`.CommandBand`
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def id(self):
        """Band identifier."""
        if self._proto.HasField("id"):
            return self._proto.id
        return None

    @property
    def band_type(self):
        """Type of band."""
        return timeline_pb2.TimelineBandType.Name(self._proto.type)

    @property
    def name(self):
        """Name of this band."""
        return self._proto.name

    @name.setter
    def name(self, value):
        self._proto.name = value

    @property
    def description(self):
        """Description of this band."""
        return self._proto.description

    @description.setter
    def description(self, value):
        self._proto.description = value

    def _set_integer_property(self, key, value):
        if not isinstance(value, int):
            raise ValueError("Provided value is not integer")
        self._proto.properties[key] = str(value)

    def _get_integer_property(self, key):
        return int(self._proto.properties[key])

    def _set_boolean_property(self, key, value):
        if not isinstance(value, boolean):
            raise ValueError("Provided value is not boolean")
        self._proto.properties[key] = "true" if value else "false"

    def _get_boolean_property(self, key):
        return self._proto.properties[key] == "true"

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
    def timezone(self):
        """
        IANA timezone name.

        Corresponds with the third column of the following table:
        https://data.iana.org/time-zones/data/zone1970.tab

        In addition, the name `UTC` is supported.
        """
        return self._proto.properties["timezone"]

    @timezone.setter
    def timezone(self, value):
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
    def height(self):
        """Spacer height"""
        return self._get_integer_property("height")

    @height.setter
    def height(self, value):
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
        merged.properties["spaceBetweenItems"] = "0"
        merged.properties["spaceBetweenLines"] = "2"
        if proto:
            merged.MergeFrom(proto)
        super(ItemBand, self).__init__(merged)

    @property
    def frozen(self):
        """
        Fix this line to the top of the view. Frozen bands are always
        rendered above other bands.
        """
        return self._get_boolean_property("frozen")

    @frozen.setter
    def frozen(self, value):
        self._set_boolean_property("frozen", value)

    @property
    def tags(self):
        """
        Item tags that this band filters on.

        :type: str[]
        """
        return self._proto.tags

    @tags.setter
    def tags(self, value):
        self._proto.tags[:] = value

    @property
    def item_background_color(self):
        """CSS color string."""
        return self._proto.properties["itemBackgroundColor"]

    @item_background_color.setter
    def item_background_color(self, value):
        self._proto.properties["itemBackgroundColor"] = value

    @property
    def item_border_color(self):
        """CSS color string."""
        return self._proto.properties["itemBorderColor"]

    @item_border_color.setter
    def item_border_color(self, value):
        self._proto.properties["itemBorderColor"] = value

    @property
    def item_border_width(self):
        return self._get_integer_property("itemBorderWidth")

    @item_border_width.setter
    def item_border_width(self, value):
        self._set_integer_property("itemBorderWidth", value)

    @property
    def item_corner_radius(self):
        return self._get_integer_property("itemCornerRadius")

    @item_corner_radius.setter
    def item_corner_radius(self, value):
        self._set_integer_property("itemCornerRadius", value)

    @property
    def item_height(self):
        return self._get_integer_property("itemHeight")

    @item_height.setter
    def item_height(self, value):
        self._set_integer_property("itemHeight", value)

    @property
    def item_margin_left(self):
        return self._get_integer_property("itemMarginLeft")

    @item_margin_left.setter
    def item_margin_left(self, value):
        self._set_integer_property("itemMarginLeft", value)

    @property
    def item_text_color(self):
        """CSS color string."""
        return self._proto.properties["itemTextColor"]

    @item_text_color.setter
    def item_text_color(self, value):
        self._proto.properties["itemTextColor"] = value

    @property
    def item_text_overflow(self):
        """One of ``show``, ``clip``, or ``hide``."""
        return self._proto.properties["itemTextOverflow"]

    @item_text_overflow.setter
    def item_text_overflow(self, value):
        self._proto.properties["itemTextOverflow"] = value

    @property
    def item_text_size(self):
        return self._get_integer_property("itemTextSize")

    @item_text_size.setter
    def item_text_size(self, value):
        self._set_integer_property("itemTextSize", value)

    @property
    def margin_bottom(self):
        return self._get_integer_property("marginBottom")

    @margin_bottom.setter
    def margin_bottom(self, value):
        self._set_integer_property("marginBottom", value)

    @property
    def margin_top(self):
        return self._get_integer_property("marginTop")

    @margin_top.setter
    def margin_top(self, value):
        self._set_integer_property("marginTop", value)

    @property
    def multiline(self):
        """
        Draw items on multiple lines if otherwise there would be collisions.
        """
        return self._get_boolean_property("multiline")

    @multiline.setter
    def multiline(self, value):
        self._set_boolean_property("multiline", value)

    @property
    def space_between_items(self):
        """
        In case of multilining, this indicates the minimum horizontal space
        between items. If an item does not meet this treshold, it gets
        rendered on a different line.
        """
        return self._get_integer_property("spaceBetweenItems")

    @space_between_items.setter
    def space_between_items(self, value):
        self._set_integer_property("spaceBetweenItems", value)

    @property
    def space_between_lines(self):
        """
        In case of multilining, this indicates the vertical space between
        lines.
        """
        return self._get_integer_property("spaceBetweenLines")

    @space_between_lines.setter
    def space_between_lines(self, value):
        self._set_integer_property("spaceBetweenLines", value)
