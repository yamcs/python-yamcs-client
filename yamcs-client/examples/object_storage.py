from __future__ import print_function

from yamcs import storage
from yamcs.core import GLOBAL_INSTANCE


def print_buckets(instance):
    for bucket in client.list_buckets(instance=instance):
        print(' {} ({} objects, {} bytes)'.format(
            bucket, bucket.object_count, bucket.size))
        listing = bucket.list_objects()
        print ('  prefixes:', listing.prefixes)
        for obj in listing.objects:
            print('  object:', obj)


if __name__ == '__main__':
    client = storage.Client('localhost:8090')

    print('Buckets:')
    print_buckets(instance='simulator')

    print('\nGlobal buckets:')
    print_buckets(instance=GLOBAL_INSTANCE)
