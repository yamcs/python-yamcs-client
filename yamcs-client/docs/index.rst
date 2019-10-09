Yamcs Client Library for Python
===============================

Getting Started
---------------

Install Python 3.5 or higher.

If necessary, you can also use Python 2.7, but be aware that this final 2.x version will soon reach its long anticipated `End Of Life <https://www.python.org/dev/peps/pep-0373/>`_ date. Python versions lower than 2.7 are already EOL and therefore *not* supported.

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
* :doc:`storage/index`

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
    storage/index
    examples/index
