class Parameter(object):

    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        return self._proto.name
    
    @property
    def qualified_name(self):
        return self._proto.qualifiedName
