TM/TC
=====

The Mission Database API provides methods that you can use to programmatically retrieve the content of a Yamcs Mission Database (MDB).

Usage
-----

Query the Mission Database:

.. code-block:: python

    from yamcs.tmtc import ProcessorClient

    client = ProcessorClient('localhost:8090')

    for parameter in client.list_parameters():
        print(parameter.qualifiedName)


Fetch the MDB definition of a single item:

.. code-block:: python

    from yamcs.mdb import MDBClient

    client = MDBClient('localhost', 8090, instance='simulator')

    voltage1 = client.get_parameter('/YSS/SIMULATOR/BatteryVoltage1')

ProcessorClient
---------------

