Timeline
========

The Timeline API allows for scheduling and managing time-based data in Yamcs. This includes high-level organizational **Views**, the **Bands** they contain, and the individual **Items** (such as Activities) within those bands.

The :class:`.TimelineClient` provides the interface to interact with these resources:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient("localhost:8090")
    timeline = client.get_timeline_client(instance="simulator")


Conceptual Model
----------------

*   **View**: A top-level container used to group multiple bands together for a specific purpose (e.g., "Daily Operations").
*   **Band**: A horizontal lane within a view. Bands can be of different types and act as filters or containers for items.
*   **Item**: The actual data points on the timeline. These are often activities (like those defined in :doc:`../activities/index`) or simple events with a start time and duration.


Timeline Items
--------------

Within the Yamcs timeline, Items are the fundamental building blocks of a schedule. While they all share common properties like tags, durations, and start conditions, they differ in how they are executed and their intended purpose.

Here is a breakdown of the different kinds of items:

* A :class:`.TimelineActivity` is an executable item that carries a specific payload (an :doc:`Activity definition <../activities/index>`). It represents a concrete action that Yamcs can perform automatically, such as sending a **Telecommand**, running a **Python script**, or triggering a **Stack**. When the start condition is met and ``auto_start`` is enabled, Yamcs handles the execution logic internally.

* A :class:`.TimelineTask` represents a manual or user-driven action. Unlike activities, tasks are usually "placeholders" for work to be performed by an operator.

  * **Manual Lifecycle:** They have ``auto_start`` disabled by default, meaning an operator must manually signal when the task has started and finished via the Web UI or API.
  * **Planning:** They are primarily used for coordination and ensuring that human-in-the-loop procedures are accounted for within the mission timeline.

* A :class:`.TimelineEvent` is typically a passive marker. It is used to denote a point in time or a span of time that is significant for the mission—such as an "Orbital Sunset" or a "Communication Window", but does not involve the execution of any activities.

Create some items (any of subclasses :class:`.TimelineEvent`, :class:`.TimelineTask` or :class:`.TimelineActivity`). Bands of type :class:`.ItemBand` will display items with matching tags:

.. literalinclude:: ../../yamcs-client/examples/timeline.py
    :pyobject: create_items
    :start-after: """
    :dedent: 4


Chaining Activities
-------------------

Yamcs supports relative scheduling through **Predecessors**. This allows you to chain items together so that an activity only begins once its predecessor has met a specific condition (e.g., successful completion).

When creating a :class:`.TimelineActivity` or :class:`.TimelineTask`, the ``start`` argument can accept a **Trigger** instead of a fixed ``datetime``. There are four primary trigger types:

*   :class:`.OnSuccess`: Starts the item only if the predecessor completes successfully.
*   :class:`.OnFailure`: Starts the item only if the predecessor fails.
*   :class:`.OnCompletion`: Starts the item regardless of whether the predecessor succeeded or failed.
*   :class:`.OnStart`: Starts the item as soon as the predecessor begins (parallel execution).

.. literalinclude:: ../../yamcs-client/examples/timeline_activities.py
    :pyobject: chain_activities
    :start-after: """
    :dedent: 4


Auto-Start
----------

*   If ``auto_start=True``, Yamcs will automatically trigger the execution logic the moment the relationship conditions are satisfied. This is enabled by default for :class:`.TimelineActivity` instances.
*  If ``auto_start=False``, Yamcs will wait for a user to manually "Start" the item in the Web UI, unless specifically configured otherwise. This is the default for :class:`.TimelineTask`.

:class:`.TimelineEvent` classes do not have such a configuration option: they always start on time.


Bands
-----

A **Band** is a horizontal lane on the timeline. It defines what data is displayed and how that data is visualized. Bands do not "own" items; instead, they act as filters or data providers.

The timeline supports several specialized band types:

* :class:`.TimeRuler`: Displays absolute time, formatted in a timezone of choice.
* :class:`.ItemBand`: The most common band. It displays :class:`Item` resources (Activities, Tasks, Events) based on matching **tags**.
* :class:`.CommandBand`: Automatically displays telecommands that have been issued to the system, providing a historical record of commanding.
* :class:`.ParameterPlot`: Plots the values of a numeric parameter.
* :class:`.ParameterStateBand`: Visualizes the state of a specific telemetry parameter over time (e.g., "On/Off" or "Nominal/Warning").
* :class:`.Spacer`: Insert vertical gap between surrounding bands.

Create a few :class:`.Band` objects, matching the tags of the previously created timeline events.

.. literalinclude:: ../../yamcs-client/examples/timeline.py
    :pyobject: create_bands
    :start-after: global
    :dedent: 4


Views
-----

A :class:`.View` is a top-level organizational container. It represents a specific layout that a user opens in the Yamcs Web UI. A View consists of an ordered list of **Bands**:

Create a :class:`.View` showing all bands:

.. literalinclude:: ../../yamcs-client/examples/timeline.py
    :pyobject: create_view
    :start-after: """
    :dedent: 4

Create a view with :class:`.ParameterStateBand` and :class:`.ParameterPlot` bands:

.. literalinclude:: ../../yamcs-client/examples/timeline.py
    :pyobject: create_parameter_bands
    :start-after: """
    :dedent: 4


Reference
---------

.. toctree::
    :maxdepth: 2

    client
    model
