from yamcs.core.client import BaseClient
from yamcs.mdb.client import MDBClient
from yamcs.tmtc.client import ProcessorClient


class YamcsClient(BaseClient):
    """
    Client for accessing core Yamcs resources.

    The only state managed by this client is its connection info to Yamcs.

    :param str address: The address to the Yamcs server in the format 'host:port'
    """

    def __init__(self, address, **kwargs):
        super(YamcsClient, self).__init__(address, **kwargs)

    def get_mdb(self, instance):
        """
        Return an object for working with the MDB for the specified instance.

        :param str instance: A Yamcs instance name.
        """
        return MDBClient(self, instance)

    def get_processor(self, instance, processor):
        """
        Return an object for working with a specific Yamcs processor.

        :param str instance: A Yamcs instance name.
        :param str processor: A processor name within that instance.
        """
        return ProcessorClient(self, instance, processor)
