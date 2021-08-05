from yamcs.client import YamcsClient

client = YamcsClient("localhost:8090")
client.create_instance(
    "blub", template="abc", args={"port": "8888"}, labels={"foo": "bar", "bar": "baz"}
)
