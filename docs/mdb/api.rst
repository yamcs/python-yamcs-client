Mission Database
================

The Mission Database API provides methods that you can use to programmatically retrieve the content of a Yamcs Mission Database (MDB).

.. note::

    This API does not currently provide offline access to an MDB export.

Usage
-----

Query the Mission Database:

.. code-block:: python

    from yamcs.mdb import MDBClient

    client = MDBClient('localhost:8090')

    # Get the resource name for the MDB of a particular instance
    mdb = client.mdb_path(instance='simulator')

    for parameter in client.list_parameters(mdb):
        print(parameter.qualifiedName)

    for command in mdb_client.list_commands(mdb):
        print(command.qualifiedName)


Fetch the MDB definition of a single item:

.. code-block:: python

    from yamcs.mdb import MDBClient

    client = MDBClient('localhost:8090')

    # Get the resource name for the MDB of a particular instance
    mdb = client.mdb_path(instance='simulator')

    voltage1 = client.get_parameter(mdb, '/YSS/SIMULATOR/BatteryVoltage1')

.. autopb2:: hah3

MDBClient
---------

.. autoclass:: yamcs.mdb.MDBClient
    :members:
    :undoc-members:
    :show-inheritance:

ParameterInfo
-------------

.. class:: yamcs.types.mdb_pb2.ParameterInfo

    .. attribute:: qualifiedName
