Object Storage
==============

The Storage API provides methods that you can use to programmatically work with Yamcs buckets and objects.

Reference
---------

.. toctree::

    client
    model


Snippets
--------

Create a :class:`.StorageClient` for a specific instance:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    storage = client.create_storage_client()
