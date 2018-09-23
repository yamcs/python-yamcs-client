from yamcs.protobuf.mdb import mdb_pb2


class Algorithm(object):

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

    def __str__(self):
        return self.qualified_name


class Command(object):

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

    def __str__(self):
        return self.qualified_name


class Container(object):

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

    def __str__(self):
        return self.qualified_name


class Parameter(object):
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
    def data_source(self):
        """Specifies how this parameter originated (example: ``TELEMETERED``)"""
        if self._proto.HasField('dataSource'):
            return mdb_pb2.DataSourceType.Name(self._proto.dataSource)
        return None

    def __str__(self):
        return self.qualified_name


class SpaceSystem(object):
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

    def __str__(self):
        return self.qualified_name
