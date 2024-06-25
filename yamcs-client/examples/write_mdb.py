from yamcs.client import NotFound, YamcsClient

"""
The following example requires a _writable_ system.

In this example the system ``/myproject/test`` is writable, whereas
the top-level system ``/myproject`` is populated based on a predefined
XTCE file (not managed by Yamcs itself).
"""

if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    mdb = client.get_mdb(instance="myproject")

    system = "/myproject/test"
    try:
        mdb.get_parameter_type(f"{system}/float_t")
    except NotFound:
        mdb.create_parameter_type(f"{system}/float_t", eng_type="float")

    try:
        mdb.get_parameter(f"{system}/testparam")
    except NotFound:
        mdb.create_parameter(
            f"{system}/testparam",
            data_source="LOCAL",
            parameter_type=f"{system}/float_t",
        )

    # MDB is present, now publish a parameter value
    processor = client.get_processor("myproject", "realtime")
    processor.set_parameter_value(f"{system}/testparam", 123.4)
