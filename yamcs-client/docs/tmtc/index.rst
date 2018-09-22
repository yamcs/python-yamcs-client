TM/TC Processing
================

The Mission Database API provides methods that you can use to programmatically interact with a TM/TC processor.


.. toctree::

    client
    model

Snippets
--------

Create a :class:`.ProcessorClient` for a specific processor:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    processor = client.get_processor(instance='simulator', processor='realtime')


Parameter Subscription
^^^^^^^^^^^^^^^^^^^^^^

Poll latest values from a subscription:

.. literalinclude:: ../../examples/parameter-subscription.py
    :pyobject: poll_values
    :start-after: """
    :dedent: 4

Receive :class:`.ParameterData` callbacks whenever one or more of the
subscribed parameters have been updated:

.. literalinclude:: ../../examples/parameter-subscription.py
    :pyobject: receive_callbacks
    :start-after: """
    :dedent: 4

Create and modify a parameter subscription:

.. literalinclude:: ../../examples/parameter-subscription.py
    :pyobject: manage_subscription
    :start-after: """
    :dedent: 4


Commanding
^^^^^^^^^^

Issue a command:

.. literalinclude:: ../../examples/commanding.py
    :pyobject: issue_command
    :start-after: """
    :dedent: 4

Receive :class:`.CommandHistory` callbacks on command history events:

.. literalinclude:: ../../examples/commanding.py
    :pyobject: listen_to_command_history
    :start-after: """
    :dedent: 4
