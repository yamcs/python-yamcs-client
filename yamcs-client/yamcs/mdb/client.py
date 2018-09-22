from yamcs.core import pagination
from yamcs.core.helpers import adapt_name_for_rest
from yamcs.mdb.model import (Algorithm, Command, Container, Parameter,
                             SpaceSystem)
from yamcs.protobuf.mdb import mdb_pb2


class MDBClient(object):

    def __init__(self, client, instance):
        super(MDBClient, self).__init__()
        self._client = client
        self._instance = instance

    def list_space_systems(self, page_size=None):
        """
        Lists the space systems visible to this client.

        Space systems are returned in lexicographical order.

        :rtype: :class:`.SpaceSystem` iterator
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self._client,
            path='/mdb/{}/space-systems'.format(self._instance),
            params=params,
            response_class=mdb_pb2.ListSpaceSystemsResponse,
            items_key='spaceSystem',
            item_mapper=SpaceSystem,
        )

    def get_space_system(self, name):
        """
        Gets a single space system by its unique name.

        :param str name: A fully-qualified XTCE name
        :rtype: .SpaceSystem
        """
        url = '/mdb/{}/space-systems{}'.format(self._instance, name)
        response = self._client.get_proto(url)
        message = mdb_pb2.SpaceSystemInfo()
        message.ParseFromString(response.content)
        return SpaceSystem(message)

    def list_parameters(self, parameter_type=None, page_size=None):
        """Lists the parameters visible to this client.

        Parameters are returned in lexicographical order.

        :param str parameter_type: The type of parameter
        :rtype: :class:`.Parameter` iterator
        """
        params = {}

        if parameter_type is not None:
            params['type'] = parameter_type
        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self._client,
            path='/mdb/{}/parameters'.format(self._instance),
            params=params,
            response_class=mdb_pb2.ListParametersResponse,
            items_key='parameter',
            item_mapper=Parameter,
        )

    def get_parameter(self, name):
        """
        Gets a single parameter by its name.

        :param str name: Either a fully-qualified XTCE name or an alias in the
                         format ``NAMESPACE/NAME``.
        :rtype: .Parameter
        """
        name = adapt_name_for_rest(name)
        url = '/mdb/{}/parameters{}'.format(self._instance, name)
        response = self._client.get_proto(url)
        message = mdb_pb2.ParameterInfo()
        message.ParseFromString(response.content)
        return Parameter(message)

    def list_containers(self, page_size=None):
        """
        Lists the containers visible to this client.

        Containers are returned in lexicographical order.

        :rtype: :class:`.Container` iterator
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self._client,
            path='/mdb/{}/containers'.format(self._instance),
            params=params,
            response_class=mdb_pb2.ListContainersResponse,
            items_key='container',
            item_mapper=Container,
        )

    def get_container(self, name):
        """
        Gets a single container by its unique name.

        :param str name: Either a fully-qualified XTCE name or an alias in the
                         format ``NAMESPACE/NAME``.
        :rtype: .Container
        """
        name = adapt_name_for_rest(name)
        url = '/mdb/{}/containers{}'.format(self._instance, name)
        response = self._client.get_proto(url)
        message = mdb_pb2.ContainerInfo()
        message.ParseFromString(response.content)
        return Container(message)

    def list_commands(self, page_size=None):
        """
        Lists the commands visible to this client.

        Commands are returned in lexicographical order.

        :rtype: :class:`.Command` iterator
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self._client,
            path='/mdb/{}/commands'.format(self._instance),
            params=params,
            response_class=mdb_pb2.ListCommandsResponse,
            items_key='command',
            item_mapper=Command,
        )

    def get_command(self, name):
        """
        Gets a single command by its unique name.

        :param str name: Either a fully-qualified XTCE name or an alias in the
                         format ``NAMESPACE/NAME``.
        :rtype: .Command
        """
        name = adapt_name_for_rest(name)
        url = '/mdb/{}/commands{}'.format(self._instance, name)
        response = self._client.get_proto(url)
        message = mdb_pb2.CommandInfo()
        message.ParseFromString(response.content)
        return Command(message)

    def list_algorithms(self, page_size=None):
        """
        Lists the algorithms visible to this client.

        Algorithms are returned in lexicographical order.

        :rtype: :class:`.Algorithm` iterator
        """
        params = {}

        if page_size is not None:
            params['limit'] = page_size

        return pagination.Iterator(
            client=self._client,
            path='/mdb/{}/algorithms'.format(self._instance),
            params=params,
            response_class=mdb_pb2.ListAlgorithmsResponse,
            items_key='algorithm',
            item_mapper=Algorithm,
        )

    def get_algorithm(self, name):
        """
        Gets a single algorithm by its unique name.

        :param str name: Either a fully-qualified XTCE name or an alias in the
                         format ``NAMESPACE/NAME``.
        :rtype: .Algorithm
        """
        name = adapt_name_for_rest(name)
        url = '/mdb/{}/algorithms{}'.format(self._instance, name)
        response = self._client.get_proto(url)
        message = mdb_pb2.AlgorithmInfo()
        message.ParseFromString(response.content)
        return Algorithm(message)
