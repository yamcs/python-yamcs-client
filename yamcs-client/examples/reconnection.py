from time import sleep

from yamcs.client import ConnectionFailure, YamcsClient

"""
Subscription types are modeled as Python futures which cover
the lifetime of the underlying WebSocket call.

Therefore we can use methods like ``result()`` or
``add_done_callback(fn)`` to observe connection failures.

The following example uses ``result()`` to trigger
a delayed reconnection attempt.
"""


def print_data(data):
    for parameter in data.parameters:
        print(parameter)


while True:
    try:
        client = YamcsClient("localhost:8090")
        processor = client.get_processor("simulator", "realtime")
        subscription = processor.create_parameter_subscription(
            "/YSS/SIMULATOR/BatteryVoltage1", on_data=print_data
        )

        # Wait until WebSocket close
        subscription.result()
    except ConnectionFailure:
        print("Retrying in 5 seconds...")
        sleep(5)
