import urllib.parse
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from yamcs.client.core import pagination
from yamcs.client.core.context import Context
from yamcs.client.core.helpers import adapt_name_for_rest
from yamcs.client.mdb.model import (
    Algorithm,
    Command,
    Container,
    Parameter,
    ParameterType,
    RangeSet,
    SpaceSystem,
)
from yamcs.protobuf.mdb import mdb_pb2

__all__ = [
    "MDBClient",
]


def _set_range(ar, range: Tuple[float, float], level: mdb_pb2.AlarmLevelType):
    ar.level = level
    if range[0]:
        ar.minExclusive = range[0]
    if range[1]:
        ar.maxExclusive = range[1]


def _add_alarms(
    alarm_info: mdb_pb2.AlarmInfo,
    watch: Optional[Tuple[float, float]],
    warning: Optional[Tuple[float, float]],
    distress: Optional[Tuple[float, float]],
    critical: Optional[Tuple[float, float]],
    severe: Optional[Tuple[float, float]],
    min_violations: int,
):
    alarm_info.minViolations = min_violations

    if watch:
        ar = alarm_info.staticAlarmRange.add()
        _set_range(ar, watch, mdb_pb2.WATCH)
    if warning:
        ar = alarm_info.staticAlarmRange.add()
        _set_range(ar, warning, mdb_pb2.WARNING)
    if distress:
        ar = alarm_info.staticAlarmRange.add()
        _set_range(ar, distress, mdb_pb2.DISTRESS)
    if critical:
        ar = alarm_info.staticAlarmRange.add()
        _set_range(ar, critical, mdb_pb2.CRITICAL)
    if severe:
        ar = alarm_info.staticAlarmRange.add()
        _set_range(ar, severe, mdb_pb2.SEVERE)


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
        params: Dict[str, Any] = {"details": True}

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

    def create_parameter(
        self,
        name: str,
        data_source: str,
        short_description: Optional[str] = None,
        long_description: Optional[str] = None,
        aliases: Optional[Mapping[str, str]] = None,
        parameter_type: Optional[str] = None,
    ) -> Parameter:
        """
        Create a parameter.

        .. versionadded:: 1.9.1
           Compatible with Yamcs 5.8.8 onwards

        :param name:
            Fully qualified name of the parameter.

            Space systems that do not yet exist, will be added
            automatically.
        :param data_source:
            Where this parameter originated. One of ``TELEMETERED``,
            ``GROUND``, ``DERIVED``, ``CONSTANT``, ``LOCAL``, ``SYSTEM``,
            ``COMMAND``, ``COMMAND_HISTORY``.
        :param short_description:
            Short description (one line)
        :param long_description:
            Long description (Markdown)
        :param aliases:
            Aliases, keyed by namespace.
        :param parameter_type:
            Qualified name of a parameter type. This is optional,
            but recommended. It allows specifying units, alarms and so on.
        """
        req = mdb_pb2.CreateParameterRequest()
        req.name = name
        req.dataSource = mdb_pb2.DataSourceType.Value(data_source)
        if short_description:
            req.shortDescription = short_description
        if long_description:
            req.longDescription = long_description
        if aliases:
            for namespace, alias in aliases.items():
                req.aliases[namespace] = alias
        if parameter_type:
            req.parameterType = parameter_type

        url = f"/mdb/{self._instance}/parameters"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        proto = mdb_pb2.ParameterInfo()
        proto.ParseFromString(response.content)
        return Parameter(proto)

    def list_parameter_types(
        self, page_size: Optional[int] = None
    ) -> Iterable[ParameterType]:
        """
        Lists the parameter types visible to this client.

        Parameter types are returned in lexicographical order.

        .. versionadded:: 1.9.1
           Compatible with Yamcs 5.8.8 onwards
        """
        params = {}

        if page_size is not None:
            params["limit"] = page_size

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/mdb/{self._instance}/parameter-types",
            params=params,
            response_class=mdb_pb2.ListParameterTypesResponse,
            items_key="parameterTypes",
            item_mapper=ParameterType,
        )

    def get_parameter_type(self, name: str) -> ParameterType:
        """
        Gets a single parameter type by its name.

        .. versionadded:: 1.9.1
           Compatible with Yamcs 5.8.8 onwards

        :param name:
            Either a fully-qualified XTCE name or an alias in the
            format ``NAMESPACE/NAME``.
        """
        name = adapt_name_for_rest(name)
        url = f"/mdb/{self._instance}/parameter-types{name}"
        response = self.ctx.get_proto(url)
        message = mdb_pb2.ParameterTypeInfo()
        message.ParseFromString(response.content)
        return ParameterType(message)

    def create_parameter_type(
        self,
        name: str,
        eng_type: str,
        short_description: Optional[str] = None,
        long_description: Optional[str] = None,
        aliases: Optional[Mapping[str, str]] = None,
        unit: Optional[str] = None,
        signed: Optional[bool] = None,
        enum_values: Optional[Mapping[int, str]] = None,
        one_string_value: Optional[str] = None,
        zero_string_value: Optional[str] = None,
        default_alarm: Optional[RangeSet] = None,
        context_alarms: Optional[Mapping[str, RangeSet]] = None,
    ) -> ParameterType:
        """
        Create a parameter type.

        .. versionadded:: 1.9.1
           Compatible with Yamcs 5.8.8 onwards

        :param name:
            Fully qualified name of the parameter type.

            Space systems that do not yet exist, will be added
            automatically.
        :param eng_type:
            Engineering type. One of ``float``, ``integer``, ``boolean``,
            ``binary``, ``string`` or ``enumeration``.
        :param short_description:
            Short description (one line)
        :param long_description:
            Long description (Markdown)
        :param aliases:
            Aliases, keyed by namespace.
        :param unit:
            Engineering unit
        :param signed:
            Whether the engineering type supports signed representation.
            (only used with ``integer`` parameter types)
        :param enum_values:
            Enumeration labels, keyed by integer value
            (only used with ``enumeration`` parameter types)
        :param one_string_value:
            String representation of a boolean one.
            (only used with ``boolean`` parameter types)
        :param zero_string_value:
            String representation of a boolean zero.
            (only used with ``boolean`` parameter types)
        :param default_alarm:
            Default alarm, effective when no contextual alarm takes precedence.
        :param context_alarms:
            Contextual alarms, keyed by condition.
        """
        req = mdb_pb2.CreateParameterTypeRequest()
        req.name = name
        req.engType = eng_type
        if short_description:
            req.shortDescription = short_description
        if long_description:
            req.longDescription = long_description
        if aliases:
            for namespace, alias in aliases.items():
                req.aliases[namespace] = alias
        if unit:
            req.unit = unit
        if signed is not None:
            req.signed = signed
        if enum_values:
            for value, label in enum_values.items():
                enum_value = req.enumerationValues.add()
                enum_value.value = value
                enum_value.label = label
        if one_string_value:
            req.oneStringValue = one_string_value
        if zero_string_value:
            req.zeroStringValue = zero_string_value
        if default_alarm:
            _add_alarms(
                req.defaultAlarm,
                default_alarm.watch,
                default_alarm.warning,
                default_alarm.distress,
                default_alarm.critical,
                default_alarm.severe,
                default_alarm.min_violations,
            )
        if context_alarms:
            for context, alarm in context_alarms.items():
                context_alarm = req.contextAlarms.add()
                context_alarm.context = context
                _add_alarms(
                    context_alarm.alarm,
                    alarm.watch,
                    alarm.warning,
                    alarm.distress,
                    alarm.critical,
                    alarm.severe,
                    alarm.min_violations,
                )

        url = f"/mdb/{self._instance}/parameter-types"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        proto = mdb_pb2.ParameterTypeInfo()
        proto.ParseFromString(response.content)
        return ParameterType(proto)

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
