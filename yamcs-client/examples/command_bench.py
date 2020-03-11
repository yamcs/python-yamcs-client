import sys

from yamcs.client import YamcsClient

if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    processor = client.get_processor('simulator', 'realtime')

    conn = processor.create_command_connection()

    while True:
        command = conn.issue('/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF', args={
            'voltage_num': 1,
        })

        sys.stdout.write(command.id)
        sys.stdout.write(' ... ')
        sys.stdout.flush()

        ack = command.await_acknowledgment('Acknowledge_Queued')
        sys.stdout.write(str(ack))
        sys.stdout.write(' ... ')
        sys.stdout.flush()

        if ack.status == 'OK':
            ack = command.await_acknowledgment('Acknowledge_Sent')
            sys.stdout.write(str(ack))
            sys.stdout.write(' ... ')
            sys.stdout.flush()

        command.await_complete()
        sys.stdout.write('complete\n')
        sys.stdout.flush()
