from yamcs.core import pagination
from yamcs.core.helpers import adapt_name_for_rest
from yamcs.protobuf.mdb import mdb_pb2


class ArchiveClient(object):

    def __init__(self, client, instance):
        super(ArchiveClient, self).__init__()
        self._client = client
        self._instance = instance

    def calculate_completeness(self, start, stop):
        """
        Calculates the percentual completion of a range.

        Parameters are returned in lexicographical order.

        :param str parameter_type: (Optional) The type of parameter
        :rtype: ParameterInfo iterator
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
        )

    def get_parameter(self, name):
        """
        Gets a single parameter by its name.

        :param str name: Either a fully-qualified XTCE name or an alias in the
                         format ``NAMESPACE/NAME``.
        """
        name = adapt_name_for_rest(name)
        url = '/mdb/{}/parameters{}'.format(self._instance, name)
        response = self._client.get_proto(url)
        message = mdb_pb2.ParameterInfo()
        message.ParseFromString(response.content)
        return message
