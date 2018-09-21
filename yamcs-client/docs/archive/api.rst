Archive
=======

The Archive API provides methods that you can use to programmatically retrieve the content of a Yamcs Archive.

Usage
-----

Query the Mission Database:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    archive = client.get_archive('simulator')

    for parameter in client.list_parameters():
        print(parameter.qualifiedName)


Reference
---------

ArchiveClient
^^^^^^^^^^^^^

.. autoclass:: yamcs.archive.ArchiveClient
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
