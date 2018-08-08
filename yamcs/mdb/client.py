from yamcs.core import pagination
from yamcs.core.client import BaseClient
from yamcs.types import mdb_pb2


def _adapt_name_for_rest(name):
    """
    Modifies a user-provided name for use in API calls.
    Basically we want an alias like 'MDB:OPS Name/SIMULATOR_BatteryVoltage2'
    to be prepended with a slash.
    """
    if name.startswith('/'):
        return name
    elif not '/' in name:
        raise ValueError('Provided name is not a fully-qualified XTCE name.')
    return '/' + name


class MDBClient(BaseClient):
    """
    Client for accessing a Mission Database served by Yamcs.

    The only state managed by this client is its connection info to Yamcs. Therefore a
    single client may be used to access the content of any number of available MDBs.

    :param str address: The address to the Yamcs server in the format 'host:port'
    """

    @classmethod
    def mdb_path(cls, instance):
        """
        Return a fully-qualified MDB resource string
        """
        return 'mdb/' + instance

    def __init__(self, address, credentials=None):
        super(MDBClient, self).__init__(
            address, credentials=credentials)

    def list_space_systems(self, parent, page_size=None):
        """
        Lists the space systems visible to this client.

        Space systems are returned in lexicographical order.

        :param str parent: The MDB resource name
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

    def get_space_system(self, parent, name):
        """
        Gets a single space system by its unique name.

        :param str parent: The MDB resource name
        :param str name: A fully-qualified XTCE name
        """
        url = '{}/space-systems{}'.format(parent, name)
        response = self._get_proto(url)
        message = mdb_pb2.SpaceSystemInfo()
        message.ParseFromString(response.content)
        return message

    def list_parameters(self, parent, parameter_type=None, page_size=None):
        """Lists the parameters visible to this client.

        Parameters are returned in lexicographical order.

        :param str parent: The MDB resource name
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

    def get_parameter(self, parent, name):
        """
        Gets a single parameter by its name.

        :param str parent: The MDB resource name
        :param str name: Either a fully-qualified XTCE name or an alias in the
                         format ``NAMESPACE/NAME``.
        """
        name = _adapt_name_for_rest(name)
        url = '{}/parameters{}'.format(parent, name)
        response = self._get_proto(url)
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

    def get_container(self, parent, name):
        """
        Gets a single container by its unique name.

        :param str parent: The MDB resource name
        :param str name: Either a fully-qualified XTCE name or an alias in the
                         format ``NAMESPACE/NAME``.
        """
        name = _adapt_name_for_rest(name)
        url = '{}/containers{}'.format(parent, name)
        response = self._get_proto(url)
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

    def get_command(self, parent, name):
        """
        Gets a single command by its unique name.

        :param str parent: The MDB resource name
        :param str name: Either a fully-qualified XTCE name or an alias in the
                         format ``NAMESPACE/NAME``.
        """
        name = _adapt_name_for_rest(name)
        url = '{}/commands{}'.format(parent, name)
        response = self._get_proto(url)
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

    def get_algorithm(self, parent, name):
        """
        Gets a single algorithm by its unique name.

        :param str parent: The MDB resource name
        :param str name: Either a fully-qualified XTCE name or an alias in the
                         format ``NAMESPACE/NAME``.
        """
        name = _adapt_name_for_rest(name)
        url = '{}/algorithms{}'.format(parent, name)
        response = self._get_proto(url)
        message = mdb_pb2.AlgorithmInfo()
        message.ParseFromString(response.content)
        return message
