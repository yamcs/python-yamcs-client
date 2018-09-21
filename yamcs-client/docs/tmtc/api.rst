TM/TC
=====

The Mission Database API provides methods that you can use to programmatically retrieve the content of a Yamcs Mission Database (MDB).

Usage
-----

Query the Mission Database:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    processor = client.get_processor(instance='simulator', processor='realtime')


Reference
---------

ProcessorClient
^^^^^^^^^^^^^^^

.. autoclass:: yamcs.tmtc.client.ProcessorClient
    :members:
    :undoc-members:

IssuedCommand
^^^^^^^^^^^^^

.. autoclass:: yamcs.tmtc.model.IssuedCommand
    :members:
    :undoc-members:

ParameterData
^^^^^^^^^^^^^

.. autoclass:: yamcs.tmtc.model.ParameterData
    :members:
    :undoc-members:

ParameterValue
^^^^^^^^^^^^^^

.. autoclass:: yamcs.tmtc.model.ParameterValue
    :members:
    :undoc-members:

CommandHistorySubscriptionFuture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: yamcs.tmtc.client.CommandHistorySubscriptionFuture
    :members:
    :undoc-members:
    :show-inheritance:

ParameterSubscriptionFuture
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: yamcs.tmtc.client.ParameterSubscriptionFuture
    :members:
    :undoc-members:
    :show-inheritance:
