General Client
==============

Reference
---------

.. toctree::
    :maxdepth: 2

    client
    model
    authentication
    exceptions
    futures

Snippets
--------

Create a :class:`.YamcsClient`:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')

Provide credentials if Yamcs is secured:

.. code-block:: python

    from yamcs.client import Credentials, YamcsClient

    credentials = Credentials(username='admin', password='password')
    client = YamcsClient('localhost:8090', credentials=credentials)


Events
^^^^^^

Receive :class:`.Event` callbacks:

.. literalinclude:: ../../yamcs-client/examples/events.py
    :pyobject: listen_to_event_updates
    :start-after: """
    :dedent: 4

Send an event:

.. literalinclude:: ../../yamcs-client/examples/events.py
    :pyobject: send_event
    :start-after: """
    :dedent: 4
