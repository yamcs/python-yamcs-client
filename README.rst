yamcs-python-client
-------------------

yamcs-python-client is a Python wrapper for using yamcs' REST and WebSocket
interfaces.

Sample Usage:
=============

    >>> from yamcs.client import YamcsClient
    >>> client = YamcsClient(host='localhost', port=8090, instance='simulator')
