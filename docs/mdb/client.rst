Client
------
.. note::

    ``MDBClient`` instances are usually created via
    :func:`YamcsClient.get_mdb() <yamcs.client.YamcsClient.get_mdb>`:

    .. code-block:: python

        from yamcs.client import YamcsClient

        client = YamcsClient('localhost:8090')
        mdb = client.get_mdb(instance='simulator')
        # ...

.. autoclass:: yamcs.mdb.client.MDBClient
    :members:
    :undoc-members:
