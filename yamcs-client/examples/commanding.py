from __future__ import print_function

from time import sleep

from yamcs.client import YamcsClient


def issue_command():
    """Issue a command to turn battery 1 off."""
    command = processor.issue_command('/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF', args={
        'voltage_num': 1,
    }, comment='im a comment')
    print('Issued', command)


def listen_to_command_history():
    """Receive updates on command history updates."""
    def tc_callback(rec):
        print('TC:', rec)

    processor.create_command_history_subscription(on_data=tc_callback)


def issue_and_listen_to_command_history():
    """Listen to command history updates of a single issued command."""
    def tc_callback(rec):
        print('TC:', rec)

    command = processor.issue_command('/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF', args={
        'voltage_num': 1,
    }, comment='im a comment')
    command.create_command_history_subscription(on_data=tc_callback)


def tm_callback(delivery):
    for parameter in delivery.parameters:
        print('TM:', parameter)


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    processor = client.get_processor('simulator', 'realtime')

    print('Start to listen to command history')
    listen_to_command_history()

    print('Issue a command')
    issue_command()

    # Monitor the voltage parameter to confirm that it is 0
    subscription = processor.create_parameter_subscription([
        '/YSS/SIMULATOR/BatteryVoltage1',
    ], on_data=tm_callback)

    # Subscription is non-blocking
    sleep(20)
