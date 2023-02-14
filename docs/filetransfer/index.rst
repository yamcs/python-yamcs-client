File Transfer
=============

The File Transfer API provides methods that you can use to programmatically work with file transfers such as CFDP.

Reference
---------

.. toctree::

    client
    model


Snippets
--------

Create a :class:`.FileTransferClient` for a specific instance:

.. code-block:: python

    from yamcs.client import YamcsClient

    client = YamcsClient('localhost:8090')
    cfdp = client.get_file_transfer_client(instance='cfdp')

    # Operations are grouped by service.
    # Here: take the first available
    service = next(cfdp.list_services())

Upload a file to the specified location on the remote entity:

.. literalinclude:: ../../yamcs-client/examples/file_transfer.py
    :pyobject: upload_file
    :start-after: """
    :dedent: 4

Start file download:

.. literalinclude:: ../../yamcs-client/examples/file_transfer.py
    :pyobject: download_file
    :start-after: """
    :lines: 1-2
    :dedent: 4

Initiate transfer with non-default parameters (see `Model`):

.. literalinclude:: ../../yamcs-client/examples/file_transfer.py
    :pyobject: upload_file_extra
    :start-after: """
    :lines: 1-4
    :dedent: 4

Initiate transfer with extra transfer options:

.. literalinclude:: ../../yamcs-client/examples/file_transfer.py
    :pyobject: upload_file_options
    :start-after: """
    :lines: 1-6
    :dedent: 4


Subscribe to file list changes:

.. literalinclude:: ../../yamcs-client/examples/file_transfer.py
    :pyobject: subscribe_filelist
    :start-after: """
    :lines: 1
    :dedent: 4

Fetch file list from remote directory :

.. literalinclude:: ../../yamcs-client/examples/file_transfer.py
    :pyobject: fetch_filelist
    :start-after: """
    :lines: 1
    :dedent: 4

Get the latest saved remote file list for the given directory, and display it:

.. literalinclude:: ../../yamcs-client/examples/file_transfer.py
    :pyobject: get_filelist
    :start-after: """
    :dedent: 4


