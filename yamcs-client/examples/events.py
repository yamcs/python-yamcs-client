# fmt: off
from time import sleep

from yamcs.client import YamcsClient


def listen_to_event_updates():
    """Subscribe to events."""
    def callback(event):
        print('Event:', event)

    client.create_event_subscription(instance='simulator', on_data=callback)

    sleep(5)  # Subscription is non-blocking


def send_event():
    """Post an event."""
    client.send_event(instance='simulator', message='hello world')


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    listen_to_event_updates()

    print('Sending an event:')
    send_event()

    sleep(5)
