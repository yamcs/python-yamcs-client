from __future__ import print_function

from time import sleep

from yamcs.client import YamcsClient


def callback(message):
    print('Link Event: {}'.format(message))


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    subscription = client.create_data_link_subscription('simulator', callback)

    sleep(10)

    print('-----')
    # You don't have to use the on_data callback. You can also
    # directly retrieve the latest data link state from a local cache:
    print('Last values from cache:')
    for link in subscription.list_data_links():
        print(link)
