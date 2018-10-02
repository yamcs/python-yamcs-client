from __future__ import print_function

from yamcs import storage

if __name__ == '__main__':
    client = storage.Client('localhost:8090')

    print('Buckets:')
    for bucket in client.list_buckets(instance='simulator'):
        print(' {} ({} objects, {} bytes)'.format(
            bucket, bucket.object_count, bucket.size))
        listing = bucket.list_objects()
        print ('  prefixes:', listing.prefixes)
        for obj in listing.objects:
            print('  object:', obj)

    print('\nGlobal buckets:')
    for bucket in client.list_global_buckets():
        print(' {} ({} objects, {} bytes)'.format(
            bucket, bucket.object_count, bucket.size))
        listing = bucket.list_objects()
        print ('  prefixes:', listing.prefixes)
        for obj in listing.objects:
            print('  object:', obj)
