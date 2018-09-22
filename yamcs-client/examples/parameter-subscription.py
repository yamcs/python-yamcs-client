from __future__ import print_function

from time import sleep

from yamcs.client import YamcsClient


def poll_values():
    """Shows how to poll values from the subscription."""
    subscription = processor.create_parameter_subscription([
        '/YSS/SIMULATOR/BatteryVoltage1'
    ])

    sleep(5)
    print('Latest value:')
    print(subscription.get_value('/YSS/SIMULATOR/BatteryVoltage1'))

    sleep(5)
    print('Latest value:')
    print(subscription.get_value('/YSS/SIMULATOR/BatteryVoltage1'))


def receive_callbacks():
    """Shows how to receive callbacks on value updates."""
    def print_data(data):
        for parameter in data.parameters:
            print(parameter)

    processor.create_parameter_subscription('/YSS/SIMULATOR/BatteryVoltage1',
                                            on_data=print_data)
    sleep(5)  # Subscription is non-blocking


def manage_subscription():
    """Shows how to interact with a parameter subscription."""
    subscription = processor.create_parameter_subscription([
        '/YSS/SIMULATOR/BatteryVoltage1'
    ])

    sleep(5)

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

    print('Last values from cache:')
    print(subscription.get_value('/YSS/SIMULATOR/BatteryVoltage1'))
    print(subscription.get_value('/YSS/SIMULATOR/BatteryVoltage2'))
    print(subscription.get_value('/YSS/SIMULATOR/Alpha'))
    print(subscription.get_value('MDB:OPS Name/SIMULATOR_PrimBusVoltage1'))


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    processor = client.get_processor('simulator', 'realtime')

    print('Poll value cache')
    poll_values()

    print('\nReceive callbacks')
    receive_callbacks()

    print('\nModify the subscription')
    manage_subscription()
