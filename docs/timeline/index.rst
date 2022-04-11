Timeline
========

The Timeline API provides methods that you can use to programmatically work with Yamcs bands and items.

Reference
---------

.. toctree::

    client
    model


Snippets
--------

Create a :class:`.TimelineClient` for a specific instance:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient("localhost:8090")
    timeline = client.get_timeline_client(instance="simulator")


Create a few :class:`.Band` objects:

.. literalinclude:: ../../yamcs-client/examples/timeline.py
    :pyobject: create_bands
    :start-after: global
    :dedent: 4

Create some :class:`.Item` objects. Bands of type :class:`.ItemBand` will display items with matching tags:

.. literalinclude:: ../../yamcs-client/examples/timeline.py
    :pyobject: create_items
    :start-after: """
    :dedent: 4

Create a :class:`.View` showing all bands:

.. literalinclude:: ../../yamcs-client/examples/timeline.py
    :pyobject: create_view
    :start-after: """
    :dedent: 4

To update a :class:`.Band`, :class:`.Item` or :class:`.View` use the same save methods as for inserting. When saving or fetching these objects they are assigned a server identifier that is used to detect whether further saves require an insert or update.

.. literalinclude:: ../../yamcs-client/examples/timeline.py
    :pyobject: edit_band
    :start-after: global
    :dedent: 4

.. literalinclude:: ../../yamcs-client/examples/timeline.py
    :pyobject: edit_fetched_items
    :start-after: """
    :dedent: 4
