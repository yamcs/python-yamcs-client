Client
------

.. note::

    ``LinkClient`` instances are usually created via
    :func:`YamcsClient.get_link() <yamcs.client.YamcsClient.get_link>`:

    .. code-block:: python

        from yamcs.client import YamcsClient

        client = YamcsClient('localhost:8090')
        link = client.get_link(instance='simulator', link='udp-in')
        # ...

.. autoclass:: yamcs.client.LinkClient
    :members:
    :undoc-members:

.. autoclass:: yamcs.client.Cop1Subscription
    :members:
    :undoc-members:
    :show-inheritance:
