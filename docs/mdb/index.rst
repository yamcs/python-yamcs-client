Mission Database
================

The Mission Database API provides methods for reading the entries in
a Yamcs Mission Database (MDB). An MDB groups telemetry and command
definitions for one or more *space systems*. The MDB is used to:

    * Instruct Yamcs how to process incoming packets
    * Describe items in Yamcs Archive
    * Instruct Yamcs how to compose telecommands

Space systems form a hierarchical multi-rooted tree. Each level of the tree
may contain any number of definitions. These break down in:

    * parameters
    * containers
    * commands
    * algorithms

Entries in the Space system are addressable via a qualified name that
looks like a Unix file path. Each segment of the path contains the name of
the space system node, the final path segment is the name of the entry itself.

For example, in an MDB that contains these parameter entries::

    └── YSS
        └── SIMULATOR
            ├── BatteryVoltage1
            └── BatteryVoltage2

we find two space systems ``/YSS`` and ``/YSS/SIMULATOR`` and two parameter
entries ``/YSS/SIMULATOR/BatteryVoltage1`` and
``/YSS/SIMULATOR/BatteryVoltage2``.

Some MDB entries may also define an alias. An alias is a unique name to
address the entry under a custom namespace (unrelated to XTCE space systems).

When it comes to addressing entries via this client, it is possible to
provide either the fully-qualified XTCE name in the format
``/YSS/SIMULATOR/BatteryVoltage1`` or an alias in the format
``NAMESPACE/NAME``.


Reference
---------

.. toctree::

    client
    model


Snippets
--------

Create an :class:`.MDBClient` for a specific instance:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    mdb = client.get_mdb(instance='simulator')

Print all space systems:

.. literalinclude:: ../../examples/query_mdb.py
    :pyobject: print_space_systems
    :start-after: """
    :dedent: 4

Print all parameters of type ``float``:

.. literalinclude:: ../../examples/query_mdb.py
    :pyobject: print_parameters
    :start-after: """
    :dedent: 4

Print all commands:

.. literalinclude:: ../../examples/query_mdb.py
    :pyobject: print_commands
    :start-after: """
    :dedent: 4

Find a parameter by qualified name or alias:

.. literalinclude:: ../../examples/query_mdb.py
    :pyobject: find_parameter
    :start-after: """
    :dedent: 4
