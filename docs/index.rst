Yamcs Client Library for Python
===============================

Getting Started
---------------

Install Python 3.5 or higher.

Install ``yamcs-client`` from PyPI::

    pip install --upgrade yamcs-client


Usage
-----

Get domain-specific clients:

.. code-block:: python

    from yamcs.client import YamcsClient
    client = YamcsClient('localhost:8090')

    mdb = client.get_mdb(instance='simulator')
    # ...

    archive = client.get_archive(instance='simulator')
    # ...

    processor = client.get_processor(instance='simulator', processor='realtime')
    # ...


Documentation
~~~~~~~~~~~~~

* :doc:`general/index`
* :doc:`mdb/index`
* :doc:`tmtc/index`
* :doc:`archive/index`
* :doc:`link/index`
* :doc:`storage/index`
* :doc:`cfdp/index`

Examples
~~~~~~~~

* :doc:`examples/index`


.. toctree::
    :hidden:
    :maxdepth: 2
    :titlesonly:

    general/index
    mdb/index
    tmtc/index
    archive/index
    link/index
    storage/index
    cfdp/index
    examples/index
