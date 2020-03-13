from time import sleep

from yamcs.client import YamcsClient
from yamcs.kerberos import KerberosCredentials

if __name__ == '__main__':
    client = YamcsClient('localhost:8090', credentials=KerberosCredentials())

    while True:
        print(client.get_time('simulator'))
        sleep(1)
