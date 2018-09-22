Client
------

.. note::

    ``ArchiveClient`` instances are usually created via
    :func:`YamcsClient.get_archive() <yamcs.client.YamcsClient.get_archive>`:

    .. code-block:: python

        from yamcs.client import YamcsClient

        client = YamcsClient('localhost:8090')
        archive = client.get_archive(instance='simulator')
        # ...

.. autoclass:: yamcs.archive.client.ArchiveClient
    :members:
    :undoc-members:
