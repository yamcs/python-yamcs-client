from __future__ import print_function

from yamcs.management import ManagementClient


def callback(message):
    print('Mission time: {}'.format(message.currentTimeUTC))


if __name__ == '__main__':
    client = ManagementClient('localhost', 8090)
    future = client.subscribe_time('simulator', callback)

    # Receive subscription updates indefinitely
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
