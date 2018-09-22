Archive
=======

The Archive API provides methods that you can use to programmatically retrieve the content of a Yamcs Archive.

.. toctree::

    client
    model

Examples
--------

Query the Archive of an instance:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    archive = client.get_archive(instance='simulator')

    for name in client.list_packet_names():
        print(name)

.. literalinclude:: ../../examples/retrieve-index.py
