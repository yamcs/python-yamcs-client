File Transfer
=============

The File Transfer API provides methods that you can use to programmatically work with file transfers such as CFDP.

Reference
---------

.. toctree::

    client
    model


Snippets
--------

Create a :class:`.FileTransferClient` for a specific instance:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    cfdp = client.get_file_transfer_client(instance='cfdp')

    # Operations are grouped by service.
    # Here: take the first available
    service = next(cfdp.list_services())
