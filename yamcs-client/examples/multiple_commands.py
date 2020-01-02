from __future__ import print_function

from time import sleep

from yamcs.client import YamcsClient

# This demonstrates how to use a "command connection" for monitoring the
# lifecycle of multiple commands.

if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    processor = client.get_processor('simulator', 'realtime')

    # Start to listen to command history
    conn = processor.create_command_connection()

    commands = []

    # Submit a few commands
    for i in range(5):
        command = conn.issue('/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF', args={
            'voltage_num': 1,
        })
        commands.append(command)
        print('Issued', command)

        command = conn.issue('/YSS/SIMULATOR/SWITCH_VOLTAGE_ON', args={
            'voltage_num': 1,
        })
        commands.append(command)
        print('Issued', command)

    while True:
        print('------')
        for command in commands:
            print(command)
        sleep(5)
