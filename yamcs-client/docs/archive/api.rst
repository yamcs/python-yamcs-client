Archive
=======

The Archive API provides methods that you can use to programmatically retrieve the content of a Yamcs Archive.

Usage
-----

Query the Archive of an instance:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    archive = client.get_archive(instance='simulator')

    for name in client.list_packet_names():
        print(name)


Reference
---------

ArchiveClient
^^^^^^^^^^^^^

.. autoclass:: yamcs.archive.client.ArchiveClient
    :members:
    :undoc-members:

IndexChunk
^^^^^^^^^^

.. autoclass:: yamcs.archive.model.IndexChunk
    :members:
    :undoc-members:

IndexRecord
^^^^^^^^^^^

.. autoclass:: yamcs.archive.model.IndexRecord
    :members:
    :undoc-members:
