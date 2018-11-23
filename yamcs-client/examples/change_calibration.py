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


def set_calibrator():
    """Set the calibrator to a constant polynomial."""
    processor.set_default_calibrator('/YSS/SIMULATOR/BatteryVoltage2', 'polynomial', [30])

def reset_calibrator():
    """Reset the calibrator to the original MDB value."""
    processor.reset_calibrators('/YSS/SIMULATOR/BatteryVoltage2')

if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    processor = client.get_processor(instance='simulator',
                                     processor='realtime')

    subscribe_param()
    sleep(5)
    print('Set calibrator')
    set_calibrator()
    sleep(10)
    print('reset calibrator to original MDB value')
    reset_calibrator()
    sleep(10)
