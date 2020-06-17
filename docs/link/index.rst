Link Management
===============

The Link API provides methods that you can use to programmatically interact
with a Yamcs link.


Reference
---------

.. toctree::

    client
    model


Snippets
--------

Create a :class:`.LinkClient` for a specific link:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    link = client.get_link(instance='simulator', link='udp-in')


Enable a link:

.. literalinclude:: ../../examples/links.py
    :pyobject: enable_link
    :start-after: """
    :dedent: 4
