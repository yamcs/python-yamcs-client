from time import sleep

from yamcs.client import Credentials, YamcsClient

# For this example to work, enable security in Yamcs by
# configuring appropriate authentication modules.


def authenticate_with_username_password():
    """Authenticate by directly providing username/password to Yamcs."""
    credentials = Credentials(username="admin", password="password")
    client = YamcsClient("localhost:8090", credentials=credentials)

    for link in client.list_links("simulator"):
        print(link)


def authenticate_with_access_token(access_token):
    """Authenticate using an existing access token."""
    credentials = Credentials(access_token=access_token)
    client = YamcsClient("localhost:8090", credentials=credentials)

    for link in client.list_links("simulator"):
        print(link)


def impersonate_with_client_credentials():
    credentials = Credentials(
        client_id="cf79cfbd-ed01-4ae2-93e1-c606a2ebc36f",
        client_secret="!#?hgbu1*3",
        become="admin",
    )
    client = YamcsClient("localhost:8090", credentials=credentials)
    print("have", client.get_user_info().username)
    while True:
        print(client.get_time("simulator"))
        sleep(1)


def authenticate_with_basic_auth():
    """Authenticate by providing username/password on each request to Yamcs."""
    from yamcs.client import BasicAuthCredentials

    credentials = BasicAuthCredentials(username="admin", password="password")
    client = YamcsClient("localhost:8090", credentials=credentials)

    for link in client.list_links("simulator"):
        print(link)


if __name__ == "__main__":
    print("Authenticate with username/password")
    authenticate_with_username_password()

    print("\nImpersonate with client credentials")
    impersonate_with_client_credentials()
