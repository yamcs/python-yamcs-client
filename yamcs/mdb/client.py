from yamcs.core import pagination
from yamcs.core.client import BaseClient
from yamcs.types import mdb_pb2


class MDBClient(BaseClient):
    """
    Client for accessing a Mission Database served by Yamcs.

    An MDB groups telemetry and command definitions for one or more space systems.
    It provides a transversal role:

        * Instructs Yamcs how to process incoming packets
        * Describes items in Yamcs Archive
        * Instructs Yamcs how to compose telecommands

    Space systems form a hierarchical multi-rooted tree. Each level of the tree
    may contain any number of definitions. These break down in:

    * parameters
    * containers
    * commands
    * algorithms

    The only state managed by this client is its connection info to Yamcs. Therefore a
    single client may be used to access the content of any number of available MDBs.
    """

    @classmethod
    def mdb_path(cls, instance):
        """
        Return a fully-qualified MDB resource string
        """
        return 'mdb/' + instance

    @classmethod
    def space_system_path(cls, instance, space_system):
        """
        Return a fully-qualified space system resource string.

        :param str instance: Instance name
        :param str space_system: Either a fully-qualified XTCE name or an alias obtained
                                 via :meth:`name_alias`.
        """
        return 'mdb/{}/space-systems{}'.format(instance, space_system)

    @classmethod
    def parameter_path(cls, instance, parameter):
        """
        Return a fully-qualified parameter resource string.

        :param str instance: Instance name
        :param str parameter: Either a fully-qualified XTCE name or an alias obtained
                              via :meth:`name_alias`.
        """
        return 'mdb/{}/parameters{}'.format(instance, parameter)

    @classmethod
    def container_path(cls, instance, container):
        """
        Return a fully-qualified container resource string.

        :param str instance: Instance name
        :param str container: Either a fully-qualified XTCE name or an alias obtained
                              via :meth:`name_alias`.
        """
        return 'mdb/{}/containers{}'.format(instance, container)

    @classmethod
    def command_path(cls, instance, command):
        """
        Return a fully-qualified command resource string.

        :param str instance: Instance name
        :param str command: Either a fully-qualified XTCE name or an alias obtained
                            via :meth:`name_alias`.
        """
        return 'mdb/{}/commands{}'.format(instance, command)

    @classmethod
    def algorithm_path(cls, instance, algorithm):
        """
        Return a fully-qualified algorithm resource string.

        :param str instance: Instance name
        :param str algorithm: Either a fully-qualified XTCE name or an alias obtained
                              via :meth:`name_alias`.
        """
        return 'mdb/{}/algorithms{}'.format(instance, algorithm)

    @classmethod
    def name_alias(cls, namespace, name):
        """
        Return an alternative name of an MDB entry.

        Support for particular aliases is dependent on the MDB definition.
        Typically (and preferredly) MDB entries do not have any aliases and only
        fully qualified XTCE names are used for identification.

        Example: assume parameter with XTCE name ``/YSS/SIMULATOR/BatteryVoltage2`` is
        also uniquely known as ``SIMULATOR_BatteryVoltage2`` under the namespace
        ``MDB:OPS Name``, then you can use this alias in other methods of this
        class by obtaining its resource name via::

            alias = name_alias('MDB:OPS Name', 'SIMULATOR_BatteryVoltage2')
            resource_name = parameter_path('INSTANCE', alias)
            parameter = client.get_parameter(resource_name)

        :rtype: str
        """
        if namespace is not None:
            return '/' + namespace + '/' + name
        return name

    def __init__(self, host, port, credentials=None):
        super(MDBClient, self).__init__(
            host=host, port=port, credentials=credentials)

    def list_space_systems(self, parent, page_size=None):
        """
        Lists the space systems visible to this client.

        Space systems are returned in lexicographical order.

        :param str parent: The MDB name
        :rtype: SpaceSystemInfo iterator
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self,
            path=parent + '/space-systems',
            params=params,
            response_class=mdb_pb2.ListSpaceSystemsResponse,
            items_key='spaceSystem',
        )

    def get_space_system(self, name):
        """
        Gets a single space system by its unique name.

        :param str name: The space system name.
                         For example: ``mdb/INSTANCE_ID/space-systems/SPACE_SYSTEM_ID``
        """
        response = self._get_proto(name)
        message = mdb_pb2.SpaceSystemInfo()
        message.ParseFromString(response.content)
        return message

    def list_parameters(self, parent, parameter_type=None, page_size=None):
        """Lists the parameters visible to this client.

        Parameters are returned in lexicographical order.

        :param str parent: The MDB name
        :param str parameter_type: (Optional) The type of parameter
        :rtype: ParameterInfo iterator
        """
        params = {}

        if parameter_type is not None:
            params['type'] = parameter_type
        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self,
            path=parent + '/parameters',
            params=params,
            response_class=mdb_pb2.ListParametersResponse,
            items_key='parameter',
        )

    def get_parameter(self, name):
        """
        Gets a single parameter by its unique name.

        :param str name: The parameter name.
                         For example: ``mdb/INSTANCE_ID/parameters/PARAMETER_ID``
        """
        response = self._get_proto(name)
        message = mdb_pb2.ParameterInfo()
        message.ParseFromString(response.content)
        return message

    def list_containers(self, parent, page_size=None):
        """
        Lists the containers visible to this client.

        Containers are returned in lexicographical order.

        :param str parent: The MDB name
        :rtype: ContainerInfo iterator
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self,
            path=parent + '/containers',
            params=params,
            response_class=mdb_pb2.ListContainersResponse,
            items_key='container',
        )

    def get_container(self, name):
        """
        Gets a single container by its unique name.

        :param str name: The container name.
                         For example: ``mdb/INSTANCE_ID/containers/CONTAINER_ID``
        """
        response = self._get_proto(name)
        message = mdb_pb2.ContainerInfo()
        message.ParseFromString(response.content)
        return message

    def list_commands(self, parent, page_size=None):
        """
        Lists the commands visible to this client.

        Commands are returned in lexicographical order.

        :param str parent: The MDB name
        :rtype: CommandInfo iterator
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self,
            path=parent + '/commands',
            params=params,
            response_class=mdb_pb2.ListCommandsResponse,
            items_key='command',
        )

    def get_command(self, name):
        """
        Gets a single command by its unique name.

        :param str name: The command name.
                         For example: ``mdb/INSTANCE_ID/commands/COMMAND_ID``
        """
        response = self._get_proto(name)
        message = mdb_pb2.CommandInfo()
        message.ParseFromString(response.content)
        return message

    def list_algorithms(self, parent, page_size=None):
        """
        Lists the algorithms visible to this client.

        Algorithms are returned in lexicographical order.

        :param str parent: The MDB name
        :rtype: AlgorithmInfo iterator
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self,
            path=parent + '/algorithms',
            params=params,
            response_class=mdb_pb2.ListAlgorithmsResponse,
            items_key='algorithm',
        )

    def get_algorithm(self, name):
        """
        Gets a single algorithm by its unique name.

        :param str name: The algorithm name.
                         For example: ``mdb/INSTANCE_ID/algorithms/ALGORITHM_ID``
        """
        response = self._get_proto(name)
        message = mdb_pb2.AlgorithmInfo()
        message.ParseFromString(response.content)
        return message
