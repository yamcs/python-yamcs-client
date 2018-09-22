Yamcs Client Library for Python
===============================

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :hidden:

   general/index
   mdb/index
   tmtc/index
   archive/index
   examples/index

Getting Started
---------------

Install Python 3.4 or higher. Python 2.7 is also supported as long as it has not reached its `End Of Life <https://www.python.org/dev/peps/pep-0373/>`_ date.

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

Project Links
-------------

* `GitHub <https://github.com/yamcs/yamcs-python/tree/master/yamcs-client>`_
* `PyPI <https://pypi.org/project/yamcs-client/>`_
