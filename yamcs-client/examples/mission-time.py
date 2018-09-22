from __future__ import print_function

from time import sleep

from yamcs.client import YamcsClient


def callback(dt):
    print('Mission time:', dt)


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    subscription = client.create_time_subscription('simulator', callback)

    sleep(6)

    print('-----')
    # You don't have to use the on_data callback. You could also
    # directly retrieve the latest data link state from a local cache:
    print('Last time from cache:', subscription.time)

    # But then maybe you don't need a subscription, so do simply:
    time = client.get_time('simulator')
    print('Mission time (fresh from server)', time)
