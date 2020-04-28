# fmt: off
from datetime import datetime, timedelta

from yamcs.client import YamcsClient


def print_latest():
    """
    Prints completeness records for the last two days
    """
    now = datetime.utcnow()
    start = now - timedelta(days=2)

    # Results are returned in records per 'group'.
    # A completeness group matches with a CCSDS APID.

    # We may receive multiple groups with the same APID
    # depending on how much data there is for the selected
    # range.

    # Combine all returned pages by APID
    records_by_apid = {}
    for group in archive.list_completeness_index(start=start, stop=now):
        if group.name not in records_by_apid:
            records_by_apid[group.name] = []
        records_by_apid[group.name].extend(group.records)

    for apid, records in records_by_apid.items():
        print('APID:', apid)

        total = 0
        for rec in records:
            print('  -', rec)
            total += rec.count
        print('  --> Total packets for {}: {}'.format(apid, total))


if __name__ == '__main__':
    client = YamcsClient('localhost:8090')
    archive = client.get_archive(instance='simulator')
    print_latest()
