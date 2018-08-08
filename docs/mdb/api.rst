Mission Database
================

The Mission Database API provides methods that you can use to programmatically retrieve the content of a Yamcs Mission Database (MDB).

.. note::

    This API does not currently provide offline access to an MDB export.

An MDB groups telemetry and command definitions for one or more *space systems*. The MDB is used to:

    * Instruct Yamcs how to process incoming packets
    * Describe items in Yamcs Archive
    * Instruct Yamcs how to compose telecommands

Space systems form a hierarchical multi-rooted tree. Each level of the tree may contain any number of definitions. These break down in:

    * parameters
    * containers
    * commands
    * algorithms

Entries in the Space system are typically addressed via a qualified name that looks like a Unix file path. Each segment of the path contains the name of the space system node, the final path segment is the name of the entry itself.

For example, in an MDB that contains these parameter entries::

    └── YSS
        └── SIMULATOR
            ├── BatteryVoltage1
            └── BatteryVoltage2

we find two space systems ``/YSS`` and ``/YSS/SIMULATOR`` and two parameter entries``/YSS/SIMULATOR/BatteryVoltage1`` and ``/YSS/SIMULATOR/BatteryVoltage2``.

Some MDB entries may also define an alias. An alias is a unique name to address the entry under a custom namespace (unrelated to XTCE space systems).

When it comes to addressing entries via this API, it is usually allowed to provide either the fully-qualified XTCE name in the format ``/YSS/SIMULATOR/BatteryVoltage1`` or an alias in the format ``NAMESPACE/NAME``.


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
