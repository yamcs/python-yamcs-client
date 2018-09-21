from __future__ import print_function

from time import sleep

from yamcs.client import YamcsClient


def callback(message):
    print('Mission time: {}'.format(message.currentTimeUTC))


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    client.create_time_subscription('simulator', callback)

    # The subscription is non-blocking. Prevent the main
    # thread from exiting
    while True:
        sleep(10)
