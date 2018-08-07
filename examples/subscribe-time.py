from __future__ import print_function

from time import sleep

from yamcs.management import ManagementClient


def callback(message):
    print('Mission time: {}'.format(message.currentTimeUTC))


if __name__ == '__main__':
    client = ManagementClient('localhost', 8090)
    client.subscribe_time('simulator', callback)

    # The subscription is non-blocking. Prevent the main
    # thread from exiting
    while True:
        sleep(10)
