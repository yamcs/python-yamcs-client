Management
==========

The Management API provides methods that you can use to programmatically administer Yamcs resources.

Usage
-----

Query the Mission Database:

.. code-block:: python

    from yamcs.mdb import MDBClient

    mdb_client = MDBClient('localhost', 8090, instance='simulator')

    for parameter in mdb_client.list_parameters():
        print parameter.qualifiedName

    for command in mdb_client.list_commands():
        print command.qualifiedName


Fetch the info of a single data link:

.. code-block:: python

    from yamcs.management import ManagementClient

    client = ManagementClient('localhost', 8090)
    name = ManagementClient.data_link_path('[INSTANCE]', '[LINK]')
    response = client.get_data_link(name)

ManagementClient
----------------

.. automodule:: yamcs.management.client
    :members:
    :undoc-members:
    :show-inheritance:
