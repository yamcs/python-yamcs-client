from yamcs.protobuf.mdb import mdb_pb2


class Algorithm:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Short name"""
        return self._proto.name

    @property
    def qualified_name(self):
        """Full name (incl. space system)"""
        return self._proto.qualifiedName

    @property
    def aliases(self):
        """List of (namespace, name) pairs, as 2-tuples"""
        return {alias.namespace: alias.name for alias in self._proto.alias}.items()

    @property
    def description(self):
        """Short description."""
        if self._proto.HasField("shortDescription"):
            return self._proto.shortDescription
        return None

    @property
    def long_description(self):
        """Long description."""
        if self._proto.HasField("longDescription"):
            return self._proto.longDescription
        return None

    def __str__(self):
        return self.qualified_name


class Command:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Short name"""
        return self._proto.name

    @property
    def qualified_name(self):
        """Full name (incl. space system)"""
        return self._proto.qualifiedName

    @property
    def aliases(self):
        """List of (namespace, name) pairs, as 2-tuples"""
        return {alias.namespace: alias.name for alias in self._proto.alias}.items()

    @property
    def description(self):
        """Short description."""
        if self._proto.HasField("shortDescription"):
            return self._proto.shortDescription
        return None

    @property
    def long_description(self):
        """Long description."""
        if self._proto.HasField("longDescription"):
            return self._proto.longDescription
        return None

    @property
    def base_command(self):
        if self._proto.HasField("baseCommand"):
            return Command(self._proto.baseCommand)
        return None

    @property
    def abstract(self):
        """
        Whether this is an abstract command. Abstract commands are
        intended for inheritance and cannot be issued directly.
        """
        return self._proto.abstract

    @property
    def significance(self):
        if self._proto.HasField("significance"):
            return Significance(self._proto.significance)
        return None

    def __str__(self):
        return self.qualified_name


class Significance:
    def __init__(self, proto):
        self._proto = proto

    @property
    def consequence_level(self):
        """
        One of ``NONE``, ``WATCH``, ``WARNING``, ``DISTRESS``, ``CRITICAL``
        or ``SEVERE``.
        """
        if self._proto.HasField("consequenceLevel"):
            return mdb_pb2.SignificanceInfo.SignificanceLevelType.Name(
                self._proto.consequenceLevel
            )
        return None

    @property
    def reason(self):
        """Message attached to this significance."""
        if self._proto.HasField("reasonForWarning"):
            return self._proto.reasonForWarning
        return None

    def __str__(self):
        return f"[{self.consequence_level}] {self.reason}"


class Container:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Short name"""
        return self._proto.name

    @property
    def qualified_name(self):
        """Full name (incl. space system)"""
        return self._proto.qualifiedName

    @property
    def aliases(self):
        """List of (namespace, name) pairs, as 2-tuples"""
        return {alias.namespace: alias.name for alias in self._proto.alias}.items()

    @property
    def description(self):
        """Short description."""
        if self._proto.HasField("shortDescription"):
            return self._proto.shortDescription
        return None

    @property
    def long_description(self):
        """Long description."""
        if self._proto.HasField("longDescription"):
            return self._proto.longDescription
        return None

    def __str__(self):
        return self.qualified_name


class ArrayType:
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Short name of this type."""
        return self._proto.type.engType

    @property
    def arrayType(self):
        """
        In case the elements of an array of this type are also of type `array`, this
        returns type info of the elements' array type.

        .. note::
            This is an uncommon use case. Multi-dimensional arrays are more prevalent.

        :type: :class:`.ArrayType`
        """
        if self._proto.type.HasField("arrayInfo"):
            return ArrayType(self._proto.type.arrayInfo)
        return None

    @property
    def members(self):
        """
        In case the elements of this array are of type `aggregate`, this returns
        an ordered list of its direct sub-members.

        :type: List[:class:`.Member`]
        """
        return [Member(member) for member in self._proto.type.member]

    @property
    def dimensions(self):
        """The number of dimensions in case of a multi-dimensional array."""
        if self._proto.HasField("dimensions"):
            return self._proto.dimensions

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
    def name(self):
        """Short name"""
        return self._proto.name

    @property
    def type(self):
        """
        Engineering type.

        :type: str
        """
        if self._proto.HasField("type"):
            return self._proto.type.engType
        return None

    @property
    def arrayType(self):
        """
        In case this member is of type `array`, this returns array-specific
        type info.

        :type: :class:`.ArrayType`
        """
        if self._proto.type.HasField("arrayInfo"):
            return ArrayType(self._proto.type.arrayInfo)
        return None

    @property
    def members(self):
        """
        In case this member is of type `aggregate`, this returns an ordered list
        of its direct sub-members.

        :type: List[:class:`.Member`]
        """
        return [Member(member) for member in self._proto.type.member]

    def __str__(self):
        return self.name


class Parameter:
    """
    From XTCE:

        A Parameter is a description of something that can have
        a value. It is not the value itself.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Short name"""
        return self._proto.name

    @property
    def qualified_name(self):
        """Full name (incl. space system)"""
        return self._proto.qualifiedName

    @property
    def aliases(self):
        """List of (namespace, name) pairs, as 2-tuples"""
        return {alias.namespace: alias.name for alias in self._proto.alias}.items()

    @property
    def description(self):
        """Short description."""
        if self._proto.HasField("shortDescription"):
            return self._proto.shortDescription
        return None

    @property
    def long_description(self):
        """Long description."""
        if self._proto.HasField("longDescription"):
            return self._proto.longDescription
        return None

    @property
    def data_source(self):
        """
        Specifies how this parameter originated (example: ``TELEMETERED``)

        :type: str
        """
        if self._proto.HasField("dataSource"):
            return mdb_pb2.DataSourceType.Name(self._proto.dataSource)
        return None

    @property
    def type(self):
        """
        Engineering type.

        :type: str
        """
        if self._proto.type.HasField("engType"):
            return self._proto.type.engType
        return None

    @property
    def arrayType(self):
        """
        In case this parameter is of type `array`, this returns array-specific
        type info.

        :type: :class:`.ArrayType`
        """
        if self._proto.type.HasField("arrayInfo"):
            return ArrayType(self._proto.type.arrayInfo)
        return None

    @property
    def members(self):
        """
        In case this parameter is of type `aggregate`, this returns an ordered list
        of its direct members.

        :type: List[:class:`.Member`]
        """
        return [Member(member) for member in self._proto.type.member]

    def __str__(self):
        return self.qualified_name


class SpaceSystem:
    """
    From XTCE:

        A SpaceSystem is a collection of SpaceSystem(s) including space assets,
        ground assets, multi-satellite systems and sub-systems.  A SpaceSystem
        is the root element for the set of data necessary to monitor and command
        an arbitrary space device - this includes the binary decomposition of
        the data streams going into and out of a device.
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        """Short name"""
        return self._proto.name

    @property
    def qualified_name(self):
        """Full name (incl. space system)"""
        return self._proto.qualifiedName

    @property
    def aliases(self):
        """List of (namespace, name) pairs, as 2-tuples"""
        return {alias.namespace: alias.name for alias in self._proto.alias}.items()

    @property
    def description(self):
        """Short description."""
        if self._proto.HasField("shortDescription"):
            return self._proto.shortDescription
        return None

    @property
    def long_description(self):
        """Long description."""
        if self._proto.HasField("longDescription"):
            return self._proto.longDescription
        return None

    def __str__(self):
        return self.qualified_name
