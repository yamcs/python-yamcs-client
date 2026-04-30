Activities
==========

Activities are executable units of work within Yamcs. They provide a structured way to trigger commands, run scripts, or execute stacks.

The Python client allows you to define these activities programmatically and schedule them on the :doc:`Yamcs Timeline <../timeline/index>`.


Core Concepts
-------------

Each activity type inherits from the base :class:`Activity` class. Yamcs currently supports three primary built-in types:

*   :class:`.CommandActivity`: Executes a single telecommand.
*   :class:`.ScriptActivity`: Runs a system script or executable.
*   :class:`.StackActivity`: Executes a pre-defined stack stored in a Yamcs bucket.


API Reference
-------------

.. autoclass:: yamcs.client.Activity
    :members:
    :undoc-members:
    :show-inheritance:

    .. note::
       This is an abstract base class. You should instantiate one of the subclasses below.

.. autoclass:: yamcs.client.CommandActivity
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: yamcs.client.ScriptActivity
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: yamcs.client.StackActivity
    :members:
    :undoc-members:
    :show-inheritance:
