from yamcs.core import pagination
from yamcs.core.client import BaseClient
from yamcs.types import mdb_pb2


class MDBClient(BaseClient):

    @classmethod
    def name_alias(cls, namespace, name):
        """
        Return a path representation of a name alias.
        """
        if namespace is not None:
            return '/' + namespace + '/' + name
        return name

    def __init__(self, host, port, credentials=None, instance=None):
        super(MDBClient, self).__init__(
            host=host, port=port, credentials=credentials)
        self.instance = instance
        self.mdb_api = '/mdb/' + instance

    def list_space_systems(self, page_size=None):
        """
        Lists the space systems visible to this client.

        Space systems are returned in lexicographical order.
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self,
            path=self.mdb_api + '/space-systems',
            params=params,
            response_class=mdb_pb2.ListSpaceSystemsResponse,
            items_key='spaceSystem',
        )

    def get_space_system(self, name):
        """
        Gets a single space system by its unique name.
        """
        response = self._get_proto('{}/space-systems{}'.format(self.mdb_api, name))
        message = mdb_pb2.SpaceSystemInfo()
        message.ParseFromString(response.content)
        return message

    def list_parameters(self, parameter_type=None, page_size=None):
        """Lists the parameters visible to this client.

        Parameters are returned in lexicographical order.

        :param str parameter_type: (Optional) The type of parameter
        """
        params = {}

        if parameter_type is not None:
            params['type'] = parameter_type
        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self,
            path=self.mdb_api + '/parameters',
            params=params,
            response_class=mdb_pb2.ListParametersResponse,
            items_key='parameter',
        )

    def get_parameter(self, name):
        """
        Gets a single parameter by its unique name.
        """
        response = self._get_proto('{}/parameters{}'.format(self.mdb_api, name))
        message = mdb_pb2.ParameterInfo()
        message.ParseFromString(response.content)
        return message

    def list_containers(self, page_size=None):
        """
        Lists the containers visible to this client.

        Containers are returned in lexicographical order.
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self,
            path=self.mdb_api + '/containers',
            params=params,
            response_class=mdb_pb2.ListContainersResponse,
            items_key='container',
        )

    def get_container(self, name):
        """
        Gets a single container by its unique name.
        """
        response = self._get_proto('{}/containers{}'.format(self.mdb_api, name))
        message = mdb_pb2.ContainerInfo()
        message.ParseFromString(response.content)
        return message

    def list_commands(self, page_size=None):
        """
        Lists the commands visible to this client.

        Commands are returned in lexicographical order.
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self,
            path=self.mdb_api + '/commands',
            params=params,
            response_class=mdb_pb2.ListCommandsResponse,
            items_key='command',
        )

    def get_command(self, name):
        """
        Gets a single command by its unique name.
        """
        response = self._get_proto('{}/commands{}'.format(self.mdb_api, name))
        message = mdb_pb2.CommandInfo()
        message.ParseFromString(response.content)
        return message

    def list_algorithms(self, page_size=None):
        """
        Lists the algorithms visible to this client.

        Algorithms are returned in lexicographical order.
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self,
            path=self.mdb_api + '/algorithms',
            params=params,
            response_class=mdb_pb2.ListAlgorithmsResponse,
            items_key='algorithm',
        )

    def get_algorithm(self, name):
        """
        Gets a single algorithm by its unique name.
        """
        response = self._get_proto('{}/algorithms{}'.format(self.mdb_api, name))
        message = mdb_pb2.AlgorithmInfo()
        message.ParseFromString(response.content)
        return message
