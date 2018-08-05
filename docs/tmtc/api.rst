TM/TC
=====

The Mission Database API provides methods that you can use to programmatically retrieve the content of a Yamcs Mission Database (MDB).

Usage
-----

Query the Mission Database:

.. code-block:: python

    from yamcs.mdb.client import MDBClient

    mdb_client = MDBClient('localhost', 8090, instance='simulator')

    for parameter in mdb_client.list_parameters():
        print parameter.qualifiedName

    for command in mdb_client.list_commands():
        print command.qualifiedName


Fetch the MDB definition of a single item:

.. code-block:: python

    from yamcs.mdb.client import MDBClient

    mdb_client = MDBClient('localhost', 8090, instance='simulator')

    voltage1 = mdb_client.get_parameter('/YSS/SIMULATOR/BatteryVoltage1')

ProcessorClient
---------------

