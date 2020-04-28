# fmt: off
from time import sleep

from yamcs.client import YamcsClient


def subscribe_param():
    """Print value of parameter"""
    def print_data(data):
        for parameter in data.parameters:
            print(parameter)

    processor.create_parameter_subscription('/YSS/SIMULATOR/BatteryVoltage2',
                                            on_data=print_data)


def set_alarms():
    """Set the default (i.e. non-contextual) limits for the parameter."""
    processor.set_default_alarm_ranges('/YSS/SIMULATOR/BatteryVoltage2',
                                       watch=(-10, 10), critical=(-100, None))


def clear_alarm_ranges():
    """
    Clear (remove) all limits for the parameter. Note that if the is an alarm
    being triggered, it is not automatically acknowledged.
    """
    processor.clear_alarm_ranges('/YSS/SIMULATOR/BatteryVoltage2')


def reset_alarms():
    """Reset the alarm limits for the parameter to the original MDB value."""
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

    print('Clear(remove) all alarms')
    clear_alarm_ranges()
    sleep(10)

    print('reset alarms to their MDB value')
    reset_alarms()
    sleep(10)
