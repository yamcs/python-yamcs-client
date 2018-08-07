from __future__ import print_function

from time import sleep

from yamcs.tmtc import ProcessorClient


def callback(message):
    print('got a message', message)


if __name__ == '__main__':

    client = ProcessorClient('localhost:8090')

    processor = client.processor_path('simulator', 'realtime')
    subscription = client.create_parameter_subscription(processor, parameters=[
        '/YSS/SIMULATOR/BatteryVoltage1',
        # client.name_alias('MDB:OPS Name', 'SIMULATOR_PrimBusVoltage1')
    ], callback=callback)

    sleep(5)

    subscription.add([
        '/YSS/SIMULATOR/Alpha',
        '/YSS/SIMULATOR/BatteryVoltage2',
    ])

    sleep(5)

    subscription.remove('/YSS/SIMULATOR/Alpha')

    sleep(10)
