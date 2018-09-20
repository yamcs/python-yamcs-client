from __future__ import print_function

from datetime import datetime, timedelta

from yamcs.client import YamcsClient
from yamcs.core.helpers import to_isostring

client = YamcsClient('localhost:8090')

archive = client.get_archive(instance='simulator')

# Print the number of packets grouped by packet name
print('Packets:')
for name in archive.list_packet_names():
    packet_count = 0
    for chunk in archive.list_packet_histogram(name):
        for rec in chunk.records:
            packet_count += rec.count
    print('  {: <40} {: >20}'.format(name, packet_count))

# Print the number of packets grouped by packet name
print()
print('Processed Parameter Groups:')
for group in archive.list_processed_parameter_groups():
    frame_count = 0
    for chunk in archive.list_processed_parameter_group_histogram(group):
        for rec in chunk.records:
            frame_count += rec.count
    print('  {: <40} {: >20}'.format(group, frame_count))

# Print the number of events grouped by source
print()
print('Events:')
for source in archive.list_event_sources():
    event_count = 0
    for chunk in archive.list_event_histogram(source):
        for rec in chunk.records:
            event_count += rec.count
    print('  {: <40} {: >20}'.format(source, event_count))

# Print the number of commands grouped by name
print()
print('Commands:')
mdb = client.get_mdb(instance='simulator')
for command in mdb.list_commands():
    count = 0
    for chunk in archive.list_command_histogram(command.qualified_name):
        for rec in chunk.records:
            count += rec.count
    print('  {: <40} {: >20}'.format(command, count))

# Print the completeness index
# (for CCSDS-style packets)
print()
print('CCSDS Completeness:')

now = datetime.utcnow()
records_by_apid = {}
for chunk in archive.list_completeness_index(start=now - timedelta(hours=1), stop=now):
    if chunk.name not in records_by_apid:
        records_by_apid[chunk.name] = []
    records_by_apid[chunk.name].extend(chunk.records)

for apid, records in records_by_apid.iteritems():
    count = 0
    for rec in records:
        count += rec.count
    print('  {: <40} {: >20}'.format(apid, count))
