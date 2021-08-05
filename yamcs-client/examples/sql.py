from yamcs.client import YamcsClient

if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    archive = client.get_archive("simulator")

    results = archive.execute_sql(
        """
        select * from tm limit 2
    """
    )

    for i, row in enumerate(results):
        if i == 0:
            print(results.columns)
        print(row)
