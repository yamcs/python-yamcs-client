Archive
=======

The Archive API provides methods that you can use to programmatically retrieve the content of a Yamcs Archive.

Reference
---------

.. toctree::

    client
    model

Snippets
--------

Create an :class:`.ArchiveClient` for a specific instance:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    archive = client.get_archive(instance='simulator')


Packet Retrieval
^^^^^^^^^^^^^^^^

Print the last 10 packets:

.. literalinclude:: ../../examples/archive_retrieval.py
    :pyobject: print_last_packets
    :start-after: """
    :dedent: 4

Print available range of archived packets:

.. literalinclude:: ../../examples/archive_retrieval.py
    :pyobject: print_packet_range
    :start-after: """
    :dedent: 4

Iterate a specific range of packets:

.. literalinclude:: ../../examples/archive_retrieval.py
    :pyobject: iterate_specific_packet_range
    :start-after: """
    :dedent: 4


Parameter Retrieval
^^^^^^^^^^^^^^^^^^^

Retrieve the last 10 values of a parameter:

.. literalinclude:: ../../examples/archive_retrieval.py
    :pyobject: print_last_values
    :start-after: """
    :dedent: 4

Iterate a specific range of values:

.. literalinclude:: ../../examples/archive_retrieval.py
    :pyobject: iterate_specific_parameter_range
    :start-after: """
    :dedent: 4


Event Retrieval
^^^^^^^^^^^^^^^

Iterate a specific range of events:

.. literalinclude:: ../../examples/archive_retrieval.py
    :pyobject: iterate_specific_event_range
    :start-after: """
    :dedent: 4


Command Retrieval
^^^^^^^^^^^^^^^^^

Retrieve the last 10 issued commands:

.. literalinclude:: ../../examples/archive_retrieval.py
    :pyobject: print_last_commands
    :start-after: """
    :dedent: 4


Histogram Retrieval
^^^^^^^^^^^^^^^^^^^

Print the number of packets grouped by packet name:

.. literalinclude:: ../../examples/archive_breakdown.py
    :pyobject: print_packet_count
    :start-after: """
    :dedent: 4

Print the number of events grouped by source:

.. literalinclude:: ../../examples/archive_breakdown.py
    :pyobject: print_event_count
    :start-after: """
    :dedent: 4

Print the number of processed parameter frames grouped by group name:

.. literalinclude:: ../../examples/archive_breakdown.py
    :pyobject: print_pp_groups
    :start-after: """
    :dedent: 4

Print the number of commands grouped by name:

.. literalinclude:: ../../examples/archive_breakdown.py
    :pyobject: print_command_count
    :start-after: """
    :dedent: 4
