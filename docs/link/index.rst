Link Management
===============

The Link API provides methods that you can use to programmatically interact
with a Yamcs link.


Reference
---------

.. toctree::
    :maxdepth: 2

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

.. literalinclude:: ../../yamcs-client/examples/links.py
    :pyobject: enable_link
    :start-after: """
    :dedent: 4

Run a link action:

.. literalinclude:: ../../yamcs-client/examples/links.py
    :pyobject: run_action
    :start-after: """
    :dedent: 4

