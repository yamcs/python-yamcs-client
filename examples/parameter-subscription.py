from __future__ import print_function

from time import sleep

from yamcs import YamcsClient


def callback(message):
    print('got a message', message)


if __name__ == '__main__':

    client = YamcsClient('localhost:8090')

    processor = client.get_processor('simulator', 'realtime')
    subscription = processor.create_parameter_subscription([
        '/YSS/SIMULATOR/BatteryVoltage1',
    ], on_delivery=callback)

    sleep(5)

    subscription.add([
        '/YSS/SIMULATOR/Alpha',
        '/YSS/SIMULATOR/BatteryVoltage2',
        'MDB:OPS Name/SIMULATOR_PrimBusVoltage1',
    ])

    sleep(5)

    subscription.remove('/YSS/SIMULATOR/Alpha')

    sleep(10)
