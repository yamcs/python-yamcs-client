from time import sleep

from yamcs.client import YamcsClient


def receive_callbacks():
    """Registers an alarm callback."""
    def callback(alarm_update):
        print('Alarm Update:', alarm_update)

    processor.create_alarm_subscription(callback)


def acknowledge_all():
    """Acknowledges all active alarms."""
    for alarm in processor.list_alarms():
        if not alarm.is_acknowledged:
            processor.acknowledge_alarm(alarm, comment='false alarm')


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    processor = client.get_processor(instance='simulator',
                                     processor='realtime')
    receive_callbacks()
    sleep(10)

    print('Acknowledging all...')
    acknowledge_all()

    # If a parameter remains out of limits, a new alarm instance is created
    # on the next value update.  So you would keep receiving callbacks on
    # the subscription.

    # The subscription is non-blocking. Prevent the main
    # thread from exiting
    while True:
        sleep(10)
