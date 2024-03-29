TM/TC Processing
================

The TM/TC API provides methods that you can use to programmatically interact
with a TM/TC processor.


Reference
---------

.. toctree::
    :maxdepth: 2

    client
    model


Snippets
--------

Create a :class:`.ProcessorClient` for a specific processor:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    processor = client.get_processor(instance='simulator', processor='realtime')


Read/Write Parameters
^^^^^^^^^^^^^^^^^^^^^

Read a single value. This returns the latest value from server cache.

.. literalinclude:: ../../yamcs-client/examples/read_write_parameters.py
    :pyobject: print_cached_value
    :start-after: """
    :dedent: 4

Read a single value, but block until a fresh value could be processed:

.. literalinclude:: ../../yamcs-client/examples/read_write_parameters.py
    :pyobject: print_realtime_value
    :start-after: """
    :dedent: 4

Read the latest value of multiple parameters at the same time:

.. literalinclude:: ../../yamcs-client/examples/read_write_parameters.py
    :pyobject: print_current_values
    :start-after: """
    :dedent: 4

Set the value of a parameter. Only some types of parameters can
be written to. This includes software parameters (local to Yamcs)
and parameters that are linked to an external system (such as
a simulator).

.. literalinclude:: ../../yamcs-client/examples/read_write_parameters.py
    :pyobject: write_value
    :start-after: """
    :dedent: 4

Set the value of multiple parameters:

.. literalinclude:: ../../yamcs-client/examples/read_write_parameters.py
    :pyobject: write_values
    :start-after: """
    :dedent: 4


Parameter Subscription
^^^^^^^^^^^^^^^^^^^^^^

Poll latest values from a subscription:

.. literalinclude:: ../../yamcs-client/examples/parameter_subscription.py
    :pyobject: poll_values
    :start-after: """
    :dedent: 4

Receive :class:`.ParameterData` callbacks whenever one or more of the
subscribed parameters have been updated:

.. literalinclude:: ../../yamcs-client/examples/parameter_subscription.py
    :pyobject: receive_callbacks
    :start-after: """
    :dedent: 4

Create and modify a parameter subscription:

.. literalinclude:: ../../yamcs-client/examples/parameter_subscription.py
    :pyobject: manage_subscription
    :start-after: """
    :dedent: 4


Commanding
^^^^^^^^^^

Issue a command (fire-and-forget):

.. literalinclude:: ../../yamcs-client/examples/commanding.py
    :pyobject: issue_command
    :start-after: """
    :dedent: 4

To monitor acknowledgments, establish a command connection first. Commands issued from this connection are automatically updated with progress status:

.. literalinclude:: ../../yamcs-client/examples/commanding.py
    :pyobject: monitor_acknowledgment
    :start-after: """
    :dedent: 4

The default Yamcs-local acknowledgments are:

* Acknowledge_Queued
* Acknowledge_Released
* Acknowledge_Sent

Custom telemetry verifiers or command links may cause additional acknowledgments to be generated.

If configured, command completion can also be monitored:

.. literalinclude:: ../../yamcs-client/examples/commanding.py
    :pyobject: monitor_command
    :start-after: """
    :dedent: 4


Alarm Monitoring
^^^^^^^^^^^^^^^^

Receive :class:`.AlarmUpdate` callbacks:

.. literalinclude:: ../../yamcs-client/examples/alarms.py
    :pyobject: receive_callbacks
    :start-after: """
    :dedent: 4

Acknowledge all active alarms:

.. literalinclude:: ../../yamcs-client/examples/alarms.py
    :pyobject: acknowledge_all
    :start-after: """
    :dedent: 4


Run a Script
^^^^^^^^^^^^

Run a custom script. The script has to be known by Yamcs. By default, this is done by placing an executable file in the :file:`etc/scripts/` directory of Yamcs.

Scripts have access to special environment variables ``YAMCS_URL``, ``YAMCS_API_KEY``,
``YAMCS_INSTANCE`` and ``YAMCS_PROCESSOR``, which is used by :func:`YamcsClient.from_environment() <yamcs.client.YamcsClient.from_environment>`


.. literalinclude:: ../../yamcs-client/examples/scripting.py
    :pyobject: run_script
    :start-after: """
    :dedent: 4

.. code-block:: python
    :caption: :file:`etc/scripts/simulate_los.sh`

    #!/usr/bin/env -S python3 -u

    import argparse
    import os
    import time

    from yamcs.client import YamcsClient

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--duration", type=float, default=60)
    args = parser.parse_args()

    client = YamcsClient.from_environment()
    processor = client.get_processor(
        instance=os.environ["YAMCS_INSTANCE"],
        processor=os.environ["YAMCS_PROCESSOR"],
    )

    print("Starting LOS")
    processor.issue_command("/TSE/simulator/start_los")
    time.sleep(args.duration)

    print("Stopping LOS")
    processor.issue_command("/TSE/simulator/stop_los")

Notice the use of ``-u`` in the shebang. This disables Python output buffering, so that print statements are immediately seen.
