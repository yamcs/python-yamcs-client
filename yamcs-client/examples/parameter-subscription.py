from __future__ import print_function

from time import sleep

from yamcs.client import YamcsClient


def print_data(data):
    for parameter in data.parameters:
        print(parameter)


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')

    processor = client.get_processor('simulator', 'realtime')
    subscription = processor.create_parameter_subscription([
        '/YSS/SIMULATOR/BatteryVoltage1',
    ], on_data=print_data)

    sleep(5)

    # Add extra items to an existing subscription
    print('Adding extra items to the existing subscription...')
    subscription.add([
        '/YSS/SIMULATOR/Alpha',
        '/YSS/SIMULATOR/BatteryVoltage2',
        'MDB:OPS Name/SIMULATOR_PrimBusVoltage1',
    ])

    sleep(5)

    print('Shrinking subscription...')
    subscription.remove('/YSS/SIMULATOR/Alpha')

    print('Cancelling the subscription...')
    subscription.cancel()

    # You don't have to use the on_data callback. You can also
    # directly retrieve the latest value update from a local cache:
    print('Last values from cache:')
    print(subscription.get_value('/YSS/SIMULATOR/BatteryVoltage1'))
    print(subscription.get_value('/YSS/SIMULATOR/BatteryVoltage2'))
    print(subscription.get_value('/YSS/SIMULATOR/Alpha'))
    print(subscription.get_value('MDB:OPS Name/SIMULATOR_PrimBusVoltage1'))
