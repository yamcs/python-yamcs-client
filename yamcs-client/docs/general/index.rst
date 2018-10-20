General Client
==============

Reference
---------

.. toctree::
    :maxdepth: 1

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

    from yamcs.client import YamcsClient
    from yamcs.core.auth import Credentials

    credentials = Credentials(username='admin', password='password')
    client = YamcsClient('localhost:8090', credentials=credentials)


Events
^^^^^^

Receive :class:`.Event` callbacks:

.. literalinclude:: ../../examples/events.py
    :pyobject: listen_to_event_updates
    :start-after: """
    :dedent: 4

Send an event:

.. literalinclude:: ../../examples/events.py
    :pyobject: send_event
    :start-after: """
    :dedent: 4


Data Links
^^^^^^^^^^

Enable all links:

.. literalinclude:: ../../examples/data_links.py
    :pyobject: enable_all_links
    :start-after: """
    :dedent: 4
