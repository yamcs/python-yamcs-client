from time import sleep

from yamcs.client import YamcsClient


def enable_all_links():
    """Enable all links."""
    for link in client.list_data_links(instance='simulator'):
        client.enable_data_link(instance=link.instance, link=link.name)


def callback(message):
    print('Link Event: {}'.format(message))


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')

    print('Enabling all links')
    enable_all_links()

    subscription = client.create_data_link_subscription('simulator', callback)

    sleep(10)

    print('-----')
    # You don't have to use the on_data callback. You could also
    # directly retrieve the latest data link state from a local cache:
    print('Last values from cache:')
    for link in subscription.list_data_links():
        print(link)
