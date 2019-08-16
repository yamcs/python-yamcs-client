from __future__ import print_function

import requests
from yamcs.client import YamcsClient
from yamcs.core.auth import Credentials

# For this example to work, enable security in Yamcs by
# setting 'enabled: true' in etc/security.yaml

# The demo simulation configuration defines a superuser
# in etc/users.yaml with username 'admin' and username
# 'password'

def authenticate_with_username_password():
    """Authenticate in by directly providing username/password to Yamcs."""
    credentials = Credentials(username='admin', password='password')
    client = YamcsClient('localhost:8090', credentials=credentials)

    for link in client.list_data_links('simulator'):
        print(link)


def authenticate_with_access_token(access_token):
    """Authenticate using an existing access token."""
    credentials = Credentials(access_token=access_token)
    client = YamcsClient('localhost:8090', credentials=credentials)

    for link in client.list_data_links('simulator'):
        print(link)


if __name__ == '__main__':
    print('Authenticate with username/password')
    authenticate_with_username_password()

    print('\nAuthenticate with access token')
    # Obtain a valid access token. In this example
    # we use Yamcs as the Authentication Server, but
    # in more complex scenarios, this token could
    # be issued by an external entity.
    r = requests.post('http://localhost:8090/auth/token', data={
        'grant_type': 'password',
        'username': 'admin',
        'password': 'password',
    })
    authenticate_with_access_token(r.json()['access_token'])
