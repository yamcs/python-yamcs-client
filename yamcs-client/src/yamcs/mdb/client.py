import urllib.parse
from typing import Iterable, Optional

from yamcs.core import pagination
from yamcs.core.context import Context
from yamcs.core.helpers import adapt_name_for_rest
from yamcs.mdb.model import Algorithm, Command, Container, Parameter, SpaceSystem
from yamcs.protobuf.mdb import mdb_pb2


class MDBClient:
    def __init__(self, ctx: Context, instance: str):
        super(MDBClient, self).__init__()
        self.ctx = ctx
        self._instance = instance

    def list_space_systems(
        self, page_size: Optional[int] = None
    ) -> Iterable[SpaceSystem]:
        """
        Lists the space systems visible to this client.

        Space systems are returned in lexicographical order.
        """
        params = {}

        if page_size is not None:
            params["limit"] = page_size

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/mdb/{self._instance}/space-systems",
            params=params,
            response_class=mdb_pb2.ListSpaceSystemsResponse,
            items_key="spaceSystems",
            item_mapper=SpaceSystem,
        )

    def get_space_system(self, name: str) -> SpaceSystem:
        """
        Gets a single space system by its unique name.

        :param name:
            A fully-qualified XTCE name. Use ``/`` for root.
        """
        encoded_name = urllib.parse.quote_plus(name)
        url = f"/mdb/{self._instance}/space-systems/{encoded_name}"
        response = self.ctx.get_proto(url)
        message = mdb_pb2.SpaceSystemInfo()
        message.ParseFromString(response.content)
        return SpaceSystem(message)

    def export_space_system(self, name: str) -> str:
        """
        Exports an XTCE description of a space system (XML format).

        .. versionadded:: 1.9.0
           Compatible with Yamcs 5.8.0 onwards

        :param name:
            A fully-qualified XTCE name. Use ``/`` for root.
        """
        encoded_name = urllib.parse.quote_plus(name)
        url = f"/mdb/{self._instance}/space-systems/{encoded_name}:exportXTCE"
        response = self.ctx.get_proto(url)
        return response.text

    def list_parameters(
        self, parameter_type: Optional[str] = None, page_size: Optional[int] = None
    ) -> Iterable[Parameter]:
        """
        Lists the parameters visible to this client.

        Parameters are returned in lexicographical order.

        :param parameter_type:
            The type of parameter
        """
        params = {"details": True}

        if parameter_type is not None:
            params["type"] = parameter_type
        if page_size is not None:
            params["limit"] = page_size

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/mdb/{self._instance}/parameters",
            params=params,
            response_class=mdb_pb2.ListParametersResponse,
            items_key="parameters",
            item_mapper=Parameter,
        )

    def get_parameter(self, name: str) -> Parameter:
        """
        Gets a single parameter by its name.

        :param name:
            Either a fully-qualified XTCE name or an alias in the
            format ``NAMESPACE/NAME``.
        """
        name = adapt_name_for_rest(name)
        url = f"/mdb/{self._instance}/parameters{name}"
        response = self.ctx.get_proto(url)
        message = mdb_pb2.ParameterInfo()
        message.ParseFromString(response.content)
        return Parameter(message)

    def list_containers(self, page_size: Optional[int] = None) -> Iterable[Container]:
        """
        Lists the containers visible to this client.

        Containers are returned in lexicographical order.
        """
        params = {}

        if page_size is not None:
            params["limit"] = page_size

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/mdb/{self._instance}/containers",
            params=params,
            response_class=mdb_pb2.ListContainersResponse,
            items_key="containers",
            item_mapper=Container,
        )

    def get_container(self, name: str) -> Container:
        """
        Gets a single container by its unique name.

        :param name:
            Either a fully-qualified XTCE name or an alias in the
            format ``NAMESPACE/NAME``.
        """
        name = adapt_name_for_rest(name)
        url = f"/mdb/{self._instance}/containers{name}"
        response = self.ctx.get_proto(url)
        message = mdb_pb2.ContainerInfo()
        message.ParseFromString(response.content)
        return Container(message)

    def list_commands(self, page_size: Optional[int] = None) -> Iterable[Command]:
        """
        Lists the commands visible to this client.

        Commands are returned in lexicographical order.
        """
        params = {}

        if page_size is not None:
            params["limit"] = page_size

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/mdb/{self._instance}/commands",
            params=params,
            response_class=mdb_pb2.ListCommandsResponse,
            items_key="commands",
            item_mapper=Command,
        )

    def get_command(self, name: str) -> Command:
        """
        Gets a single command by its unique name.

        :param name:
            Either a fully-qualified XTCE name or an alias in the
            format ``NAMESPACE/NAME``.
        """
        name = adapt_name_for_rest(name)
        url = f"/mdb/{self._instance}/commands{name}"
        response = self.ctx.get_proto(url)
        message = mdb_pb2.CommandInfo()
        message.ParseFromString(response.content)
        return Command(message)

    def list_algorithms(self, page_size: Optional[int] = None) -> Iterable[Algorithm]:
        """
        Lists the algorithms visible to this client.

        Algorithms are returned in lexicographical order.
        """
        params = {}

        if page_size is not None:
            params["limit"] = page_size

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/mdb/{self._instance}/algorithms",
            params=params,
            response_class=mdb_pb2.ListAlgorithmsResponse,
            items_key="algorithms",
            item_mapper=Algorithm,
        )

    def get_algorithm(self, name: str) -> Algorithm:
        """
        Gets a single algorithm by its unique name.

        :param name:
            Either a fully-qualified XTCE name or an alias in the
            format ``NAMESPACE/NAME``.
        """
        name = adapt_name_for_rest(name)
        url = f"/mdb/{self._instance}/algorithms{name}"
        response = self.ctx.get_proto(url)
        message = mdb_pb2.AlgorithmInfo()
        message.ParseFromString(response.content)
        return Algorithm(message)
