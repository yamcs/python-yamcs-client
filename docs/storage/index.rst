Object Storage
==============

The Storage API provides methods that you can use to programmatically work with Yamcs buckets and objects.

Reference
---------

.. toctree::
    :maxdepth: 2

    client
    model


Snippets
--------

Create a :class:`.StorageClient`:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    storage = client.get_storage_client()
