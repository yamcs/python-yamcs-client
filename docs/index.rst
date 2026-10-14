Python Yamcs Client
===================

.. rubric:: Getting Started

Install Python 3.8 or higher.

Install ``yamcs-client`` from PyPI::

    pip install --upgrade yamcs-client

For better performance when decoding large or frequent messages (for example
high-rate parameter subscriptions), include the ``protobuf`` extra::

    pip install --upgrade yamcs-client[protobuf]

This installs the official ``protobuf`` runtime, which yamcs-client then uses
instead of its bundled pure-Python copy. Any compatible ``protobuf`` package
that is already installed is used automatically, even without this extra.


.. rubric:: Usage

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


.. rubric:: Documentation

* :doc:`general/index`
* :doc:`mdb/index`
* :doc:`tmtc/index`
* :doc:`archive/index`
* :doc:`link/index`
* :doc:`storage/index`
* :doc:`filetransfer/index`
* :doc:`tco/index`
* :doc:`activities/index`
* :doc:`timeline/index`


.. rubric:: Examples

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
    filetransfer/index
    tco/index
    activities/index
    timeline/index
    examples/index
