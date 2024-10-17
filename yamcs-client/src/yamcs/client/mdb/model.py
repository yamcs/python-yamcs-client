import abc
from typing import Dict, List, Optional, Tuple

from yamcs.protobuf.mdb import mdb_pb2

__all__ = [
    "Algorithm",
    "Argument",
    "ArgumentType",
    "ArrayType",
    "Command",
    "Container",
    "DataEncoding",
    "EnumValue",
    "Member",
    "MissionDatabaseItem",
    "Parameter",
    "ParameterType",
    "RangeSet",
    "Significance",
    "SpaceSystem",
]


class MissionDatabaseItem(abc.ABC):
    """
    Superclass for MDB items. Implementations:

    * :class:`.Algorithm`
    * :class:`.Command`
    * :class:`.Container`
    * :class:`.Parameter`
    * :class:`.ParameterType`
    * :class:`.SpaceSystem`
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Short name"""
        return self._proto.name

    @property
    def qualified_name(self) -> str:
        """Full name (incl. space system)"""
        return self._proto.qualifiedName

    @property
    def aliases(self) -> Dict[str, str]:
        """Aliases, keyed by namespace"""
        return {alias.namespace: alias.name for alias in self._proto.alias}

    @property
    def aliases_dict(self) -> Dict[str, str]:
        """
        Aliases, keyed by namespace

        This method shall be deprecated in a future release. Use
        :attr:`aliases` instead.
        """
        return self.aliases

    @property
    def description(self) -> Optional[str]:
        """Short description."""
        if self._proto.HasField("shortDescription"):
            return self._proto.shortDescription
        return None

    @property
    def long_description(self) -> Optional[str]:
        """Long description."""
        if self._proto.HasField("longDescription"):
            return self._proto.longDescription
        return None

    def __str__(self):
        return self.qualified_name


class Algorithm(MissionDatabaseItem):
    def __init__(self, proto):
        super().__init__(proto)


class Command(MissionDatabaseItem):
    def __init__(self, proto):
        super().__init__(proto)

    @property
    def base_command(self) -> Optional["Command"]:
        if self._proto.HasField("baseCommand"):
            return Command(self._proto.baseCommand)
        return None

    @property
    def abstract(self) -> bool:
        """
        Whether this is an abstract command. Abstract commands are
        intended for inheritance and cannot be issued directly.
        """
        return self._proto.abstract

    @property
    def significance(self) -> Optional["Significance"]:
        if self._proto.HasField("significance"):
            return Significance(self._proto.significance)
        return None

    @property
    def arguments(self) -> List["Argument"]:
        return [Argument(pb) for pb in self._proto.argument]


class Argument:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Argument name"""
        return self._proto.name

    @property
    def description(self) -> Optional[str]:
        """Short description"""
        if self._proto.HasField("description"):
            return self._proto.description
        return None

    @property
    def initial_value(self) -> Optional[str]:
        """Initial value"""
        if self._proto.HasField("initialValue"):
            return self._proto.initialValue
        return None

    @property
    def type(self) -> "ArgumentType":
        """Argument type information"""
        return ArgumentType(self._proto.type)

    def __str__(self):
        return self.name


class ArgumentType:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Type name"""
        return self._proto.name

    @property
    def eng_type(self) -> str:
        """Engineering type"""
        return self._proto.engType

    def __str__(self):
        return self.name


class Container(MissionDatabaseItem):
    def __init__(self, proto):
        super().__init__(proto)


class Significance:
    def __init__(self, proto):
        self._proto = proto

    @property
    def consequence_level(self) -> str:
        """
        One of ``NONE``, ``WATCH``, ``WARNING``, ``DISTRESS``, ``CRITICAL``
        or ``SEVERE``.
        """
        return mdb_pb2.SignificanceInfo.SignificanceLevelType.Name(
            self._proto.consequenceLevel
        )

    @property
    def reason(self) -> Optional[str]:
        """Message attached to this significance."""
        if self._proto.HasField("reasonForWarning"):
            return self._proto.reasonForWarning
        return None

    def __str__(self):
        return f"[{self.consequence_level}] {self.reason}"


class ArrayType:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Short name of this type."""
        return self._proto.type.engType

    @property
    def array_type(self) -> Optional["ArrayType"]:
        """
        In case the elements of an array of this type are also of type `array`, this
        returns type info of the elements' array type.

        .. note::
            This is an uncommon use case. Multi-dimensional arrays are more prevalent.
        """
        if self._proto.type.HasField("arrayInfo"):
            return ArrayType(self._proto.type.arrayInfo)
        return None

    @property
    def members(self) -> List["Member"]:
        """
        In case the elements of this array are of type `aggregate`, this returns
        an ordered list of its direct sub-members.
        """
        return [Member(member) for member in self._proto.type.member]

    @property
    def dimensions(self) -> Optional[int]:
        """The number of dimensions in case of a multi-dimensional array."""
        if self._proto.HasField("dimensions"):
            return self._proto.dimensions
        return None

    def __str__(self):
        return self.name


class Member:
    """
    A member is a data structure for a specific field of a parent data type
    (either another member, or a parameter of type `aggregate`).

    This is similar to C structs. The top-level of a member hierarchy is
    a parameter of type `aggregate`.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self) -> str:
        """Short name"""
        return self._proto.name

    @property
    def type(self) -> str:
        """Engineering type."""
        return self._proto.type.engType

    @property
    def array_type(self) -> Optional[ArrayType]:
        """
        In case this member is of type `array`, this returns array-specific
        type info.
        """
        if self._proto.type.HasField("arrayInfo"):
            return ArrayType(self._proto.type.arrayInfo)
        return None

    @property
    def members(self) -> List["Member"]:
        """
        In case this member is of type `aggregate`, this returns an ordered list
        of its direct sub-members.
        """
        return [Member(member) for member in self._proto.type.member]

    def __str__(self):
        return self.name


class EnumValue:
    def __init__(self, proto):
        self._proto = proto

    @property
    def value(self) -> int:
        """Numeric value"""
        return self._proto.value

    @property
    def label(self) -> str:
        """String value"""
        return self._proto.label

    @property
    def description(self) -> Optional[str]:
        """State description"""
        if self._proto.HasField("description"):
            return self.__proto.description
        return None

    def __str__(self):
        return self.label


class DataEncoding:
    def __init__(self, proto):
        self._proto = proto

    @property
    def type(self) -> str:
        """Raw type"""
        return mdb_pb2.DataEncodingInfo.Type.Name(self._proto.type)

    @property
    def little_endian(self) -> bool:
        """True if little-endian"""
        return self._proto.littleEndian

    @property
    def bitlength(self) -> Optional[int]:
        """The size in bits"""
        if self._proto.HasField("sizeInBits"):
            return self._proto.sizeInBits
        return None

    @property
    def encoding(self) -> Optional[str]:
        """Encoding detail"""
        if self._proto.HasField("encoding"):
            return self._proto.encoding
        return None

    def __str__(self):
        return self.type


class Parameter(MissionDatabaseItem):
    """
    A Parameter is a description of something that can have
    a value. It is not the value itself.
    """

    def __init__(self, proto):
        super().__init__(proto)

    @property
    def data_source(self) -> Optional[str]:
        """
        Specifies the source of this parameter (example: ``TELEMETERED``)
        """
        if self._proto.HasField("dataSource"):
            return mdb_pb2.DataSourceType.Name(self._proto.dataSource)
        return None

    @property
    def type(self) -> Optional[str]:
        """
        Engineering type.
        """
        if self._proto.type.HasField("engType"):
            return self._proto.type.engType
        return None

    @property
    def array_type(self) -> Optional[ArrayType]:
        """
        In case this parameter is of type `array`, this returns array-specific
        type info.
        """
        if self._proto.type.HasField("arrayInfo"):
            return ArrayType(self._proto.type.arrayInfo)
        return None

    @property
    def members(self) -> List[Member]:
        """
        In case this parameter is of type `aggregate`, this returns an ordered list
        of its direct members.
        """
        return [Member(member) for member in self._proto.type.member]

    @property
    def units(self) -> List[str]:
        """
        Engineering unit(s)
        """
        return [info.unit for info in self._proto.type.unitSet]

    @property
    def enum_values(self) -> List[EnumValue]:
        """
        In case this parameter is of type `enumeration`, this returns an ordered list
        of possible values.
        """
        return [EnumValue(enumValue) for enumValue in self._proto.type.enumValue]

    @property
    def data_encoding(self) -> Optional[DataEncoding]:
        """
        Information on the raw encoding of this parameter, if applicable.
        """
        if self._proto.type.HasField("dataEncoding"):
            return DataEncoding(self._proto.type.dataEncoding)
        return None


class ParameterType(MissionDatabaseItem):
    def __init__(self, proto):
        super().__init__(proto)

    @property
    def type(self) -> str:
        """
        Engineering type.
        """
        return self._proto.engType

    @property
    def array_type(self) -> Optional[ArrayType]:
        """
        In case this parameter type is of type `array`, this returns array-specific
        type info.
        """
        if self._proto.HasField("arrayInfo"):
            return ArrayType(self._proto.arrayInfo)
        return None

    @property
    def members(self) -> List[Member]:
        """
        In case this parameter type is of type `aggregate`, this returns an ordered list
        of its direct members.
        """
        return [Member(member) for member in self._proto.member]

    @property
    def units(self) -> List[str]:
        """
        Engineering unit(s)
        """
        return [info.unit for info in self._proto.unitSet]

    @property
    def enum_values(self) -> List[EnumValue]:
        """
        In case this parameter type is of type `enumeration`, this returns an ordered
        list of possible values.
        """
        return [EnumValue(enumValue) for enumValue in self._proto.enumValue]

    @property
    def data_encoding(self) -> Optional[DataEncoding]:
        """
        Information on the raw encoding of this parameter type, if applicable.
        """
        if self._proto.HasField("dataEncoding"):
            return DataEncoding(self._proto.dataEncoding)
        return None


class SpaceSystem(MissionDatabaseItem):
    """
    From XTCE:

        A SpaceSystem is a collection of SpaceSystem(s) including space assets,
        ground assets, multi-satellite systems and sub-systems.  A SpaceSystem
        is the root element for the set of data necessary to monitor and command
        an arbitrary space device - this includes the binary decomposition of
        the data streams going into and out of a device.
    """

    def __init__(self, proto):
        super().__init__(proto)


class RangeSet:
    """
    A set of alarm ranges that apply in a specific context.
    """

    # This is the same as yamcs.client.tmtc.model.AlarmRangeSet, but
    # with the 'context' removed. Eventually, we probably want to change
    # the tmtc one to use this class too.

    def __init__(
        self,
        watch: Optional[Tuple[Optional[float], Optional[float]]] = None,
        warning: Optional[Tuple[Optional[float], Optional[float]]] = None,
        distress: Optional[Tuple[Optional[float], Optional[float]]] = None,
        critical: Optional[Tuple[Optional[float], Optional[float]]] = None,
        severe: Optional[Tuple[Optional[float], Optional[float]]] = None,
        min_violations: int = 1,
    ):
        """
        :param watch:
            Range expressed as a tuple ``(lo, hi)``
            where lo and hi are assumed exclusive.
        :param warning:
            Range expressed as a tuple ``(lo, hi)``
            where lo and hi are assumed exclusive.
        :param distress:
            Range expressed as a tuple ``(lo, hi)``
            where lo and hi are assumed exclusive.
        :param critical:
            Range expressed as a tuple ``(lo, hi)``
            where lo and hi are assumed exclusive.
        :param severe:
            Range expressed as a tuple ``(lo, hi)``
            where lo and hi are assumed exclusive.
        :param min_violations:
            Minimum violations before an alarm is
            generated.
        """
        self.watch = watch
        self.warning = warning
        self.distress = distress
        self.critical = critical
        self.severe = severe
        self.min_violations = min_violations
