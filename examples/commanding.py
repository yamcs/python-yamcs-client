from __future__ import print_function

from time import sleep

from yamcs import YamcsClient


def callback(delivery):
    for parameter in delivery.parameter:
        print('got an update', parameter)


if __name__ == '__main__':

    client = YamcsClient('localhost:8090')

    processor = client.get_processor('simulator', 'realtime')

    response = processor.issue_command('/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF', args={
        'voltage_num': 1,
    })
    print response

    subscription = processor.create_parameter_subscription([
        '/YSS/SIMULATOR/BatteryVoltage1',
    ], on_data=callback)

    sleep(10)
