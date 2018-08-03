Client library for Yamcs.

## Example:

Query the Mission Database:

    import yamcs.mdb

    mdb_client = yamcs.mdb.Client('localhost', 8090, 'simulator')
    for parameter in mdb_client.get_parameters():
        print parameter.qualifiedName

Monitor a processor:

    from yamcs.client import YamcsClient
    client = YamcsClient(host='localhost', port=8090)
