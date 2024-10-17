Client
------

.. note::

    ``ProcessorClient`` instances are usually created via
    :func:`YamcsClient.get_processor() <yamcs.client.YamcsClient.get_processor>`:

    .. code-block:: python

        from yamcs.client import YamcsClient

        client = YamcsClient('localhost:8090')
        processor = client.get_processor(instance='simulator',
                                         processor='realtime')
        # ...

.. autoclass:: yamcs.client.ProcessorClient
    :members:
    :undoc-members:

.. autoclass:: yamcs.client.CommandConnection
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: yamcs.client.AlarmSubscription
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: yamcs.client.CommandHistorySubscription
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: yamcs.client.ContainerSubscription
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: yamcs.client.ParameterSubscription
    :members:
    :undoc-members:
    :show-inheritance:
