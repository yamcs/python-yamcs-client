MDB Client
==========

.. automodule:: yamcs.mdb
  :members:
  :show-inheritance:

Query the Mission Database:

.. code-block:: python

    import yamcs.mdb

    mdb_client = yamcs.mdb.Client('localhost', 8090, 'simulator')
    for parameter in mdb_client.get_parameters():
        print parameter.qualifiedName
