from yamcs.client import YamcsClient


def print_packet_count():
    """Print the number of packets grouped by packet name."""
    for name in archive.list_packet_names():
        packet_count = 0
        for group in archive.list_packet_histogram(name):
            for rec in group.records:
                packet_count += rec.count
        print(f"  {name: <40} {packet_count: >20}")


def print_pp_groups():
    """Print the number of processed parameter frames by group name."""
    for group in archive.list_processed_parameter_groups():
        frame_count = 0
        for pp_group in archive.list_processed_parameter_group_histogram(group):
            for rec in pp_group.records:
                frame_count += rec.count
        print(f"  {group: <40} {frame_count: >20}")


def print_event_count():
    """Print the number of events grouped by source."""
    for source in archive.list_event_sources():
        event_count = 0
        for group in archive.list_event_histogram(source):
            for rec in group.records:
                event_count += rec.count
        print(f"  {source: <40} {event_count: >20}")


def print_command_count():
    """Print the number of commands grouped by name."""
    mdb = client.get_mdb(instance="simulator")
    for command in mdb.list_commands():
        total = 0
        for group in archive.list_command_histogram(command.qualified_name):
            for rec in group.records:
                total += rec.count
        print(f"  {command.qualified_name: <40} {total: >20}")


if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    archive = client.get_archive(instance="simulator")

    print("Packets:")
    print_packet_count()

    print("\nProcessed Parameter Groups:")
    print_pp_groups()

    print("\nEvents:")
    print_event_count()

    print("\nCommands:")
    print_command_count()
