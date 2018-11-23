from __future__ import print_function

from yamcs.client import YamcsClient
from time import sleep


def subscribe_param():
    """Print value of parameter"""
    def print_data(data):
        for parameter in data.parameters:
            print(parameter)

    processor.create_parameter_subscription('/YSS/SIMULATOR/BatteryVoltage2',
                                            on_data=print_data)


def set_alarms():
    processor.set_default_alarm_ranges('/YSS/SIMULATOR/BatteryVoltage2', watch=(-10, 10), critical=(-100, None))

def reset_alarms():
    processor.reset_alarm_ranges('/YSS/SIMULATOR/BatteryVoltage2')

if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    processor = client.get_processor(instance='simulator',
                                     processor='realtime')

    subscribe_param()
    sleep(5)
    print('Set alarms')
    set_alarms()
    sleep(10)
    print('reset alarms to their MDB value')
    reset_alarms()
    sleep(10)
