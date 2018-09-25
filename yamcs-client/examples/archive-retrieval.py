from __future__ import print_function

from datetime import datetime, timedelta
from itertools import islice

from yamcs.client import YamcsClient


def print_last_packets():
    """Print the last 10 packets."""
    for packet in islice(archive.list_packets(descending=True), 0, 10):
        print(packet)


def print_packet_range():
    """Print the range of archived packets."""
    first_packet = next(iter(archive.list_packets()))
    last_packet = next(iter(archive.list_packets(descending=True)))
    print('First packet:', first_packet)
    print('Last packet:', last_packet)

    td = last_packet.generation_time - first_packet.generation_time
    print('Timespan:', td)


def iterate_specific_packet_range():
    """Count the number of packets in a specific range."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)

    total = 0
    for packet in archive.list_packets(start=start, stop=now):
        total += 1
        # print(packet)
    print('Found', total, 'packets in range')


def iterate_specific_event_range():
    """Count the number of events in a specific range."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)

    total = 0
    for event in archive.list_events(start=start, stop=now):
        total += 1
        # print(event)
    print('Found', total, 'events in range')


def print_last_values():
    """Print the last 10 values."""
    iterable = archive.list_parameter_values('/YSS/SIMULATOR/BatteryVoltage1',
                                             descending=True)
    for pval in islice(iterable, 0, 10):
        print(pval)


def iterate_specific_parameter_range():
    """Count the number of parameter values in a specific range."""
    now = datetime.utcnow()
    start = now - timedelta(hours=1)

    total = 0
    for pval in archive.list_parameter_values(
            '/YSS/SIMULATOR/BatteryVoltage1', start=start, stop=now):
        total += 1
        # print(pval)
    print('Found', total, 'parameter values in range')


def print_last_commands():
    """Print the last 10 commands."""
    iterable = archive.list_command_history(descending=True)
    for entry in islice(iterable, 0, 10):
        print(entry)


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    archive = client.get_archive(instance='simulator')

    print('Last 10 packets:')
    print_last_packets()

    print('\nPacket range:')
    print_packet_range()

    print('\nIterate specific packet range:')
    iterate_specific_packet_range()

    print('\nIterate specific event range:')
    iterate_specific_event_range()

    print('\nLast 10 parameter values:')
    print_last_values()

    print('\nIterate specific parameter range:')
    iterate_specific_parameter_range()

    print('\nLast 10 commands:')
    print_last_commands()
