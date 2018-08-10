from __future__ import print_function

from time import sleep

from yamcs import YamcsClient


def tm_callback(delivery):
    for parameter in delivery.parameters:
        print('TM:', parameter)


def tc_callback(rec):
    print('TC:', rec)


if __name__ == '__main__':

    client = YamcsClient('localhost:8090')

    processor = client.get_processor('simulator', 'realtime')

    tc_subscription = processor.create_command_history_subscription(on_data=tc_callback)

    print('Issuing command')
    response = processor.issue_command('/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF', args={
        'voltage_num': 1,
    }, comment='im a comment')
    print('Issued', response)

    subscription = processor.create_parameter_subscription([
        '/YSS/SIMULATOR/BatteryVoltage1',
    ], on_data=tm_callback)

    sleep(20)
