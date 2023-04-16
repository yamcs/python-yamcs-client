Time Correlation (TCO)
======================

The Time Correlation API provides methods that you can use to programmatically interact with a Yamcs TCO service.

Reference
---------

.. toctree::
    :maxdepth: 2

    client
    model


Snippets
--------

Create a :class:`.TCOClient` for a specific instance:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    tco = client.get_tco_client(instance='pus', service='tco0')
