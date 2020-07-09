CFDP
====

The CFDP API provides methods that you can use to programmatically work with CFDP transfers.

Reference
---------

.. toctree::

    client
    model


Snippets
--------

Create a :class:`.CFDPClient` for a specific instance:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    cfdp = client.get_cfdp_client(instance='cfdp')
