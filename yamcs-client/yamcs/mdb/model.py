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
            return self._proto.dataSource
        return None

    def __str__(self):
        return self.qualified_name


class SpaceSystem(object):

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
