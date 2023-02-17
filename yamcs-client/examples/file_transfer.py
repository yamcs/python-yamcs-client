import io
import time

from yamcs.client import YamcsClient


def upload_file():
    """Snippet used in docs to initiate upload."""
    # Transfer myfile from bucket to spacecraft
    upload = service.upload(out_bucket.name, "myfile", "/CF:/mytarget")
    upload.await_complete(timeout=10)

    if not upload.is_success():
        print("Upload failure:", upload.error)
    else:
        print(f"Successfully uploaded {upload.remote_path} ({upload.size} bytes)")


def upload_file_extra():
    """Snippet used in docs to initiate upload with extra parameters."""
    # Transfer myfile, but use an alternative destination entity
    upload = service.upload(
        out_bucket.name, "myfile", "/CF:/mytarget", destination_entity="target2"
    )
    upload.await_complete(timeout=10)

    if not upload.is_success():
        print("Upload failure:", upload.error)
    else:
        print(f"Successfully uploaded {upload.remote_path} ({upload.size} bytes)")


def upload_file_options():
    """Snippet used in docs to initiate upload with extra options."""
    upload = service.upload(
        out_bucket.name, "myfile", "/CF:/mytarget", options={"reliable": True}
    )
    upload.await_complete(timeout=60)

    if not upload.is_success():
        print("Upload failure:", upload.error)
    else:
        print(f"Successfully uploaded {upload.remote_path} ({upload.size} bytes)")


def download_file():
    """Snippet used in docs to initiate download."""
    # Download todownload from the remote
    download = service.download(in_bucket.name, "todownload")
    download.await_complete(timeout=10)

    if not download.is_success():
        print("Download failure:", download.error)
    else:
        print(f"Successfully downloaded {download.remote_path} ({download.size} bytes)")


def subscribe_filelist():
    """Snippet used in docs to subscribe to filelist updates."""
    subscription = service.create_filelist_subscription(on_data=filelist_callback)
    return subscription


def filelist_callback(filelist):
    global updated
    updated = True
    print(f"Filelist updated with {len(filelist.files)} files or directories")


def fetch_filelist():
    """Snippet used in docs to fetch a remote filelist."""
    filelist_request = service.fetch_filelist("/")
    return filelist_request


def get_filelist():
    """Snippet used in docs to get a saved filelist and display it."""
    filelist_response = service.get_filelist("/")

    # Display file list
    if filelist_response:
        print("File list received:")
        if not filelist_response.files:
            print("\tEmpty file list")
        for file in filelist_response.files:
            print(f"\t{file.name + ('/' if file.is_directory else ''):<12}\
            t{str(file.size) + ' bytes':>12}\tLast Modified: {file.modified}")
    else:
        print("No filelist found")


if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    storage = client.get_storage_client()
    cfdp = client.get_file_transfer_client(instance="cfdp")

    # Use pre-existing buckets, one for each direction
    out_bucket = storage.get_bucket("cfdpUp")
    in_bucket = storage.get_bucket("cfdpDown")

    # Prepare a sample file
    file_like = io.StringIO("Sample file content")
    out_bucket.upload_object("myfile", file_like)

    # Assume only one CFDP service
    service = next(cfdp.list_services())

    # Show transfer service capabilities
    print(service.capabilities)

    # Show possible transfer options
    for option in service.transfer_options:
        print(option)

    upload_file()

    upload_file_extra()

    upload_file_options()

    download_file()

    # DIRECTORY LISTING
    updated = False

    subscribe_filelist()

    fetch_filelist()

    start = time.time()
    while not updated and time.time() - start < 20:
        time.sleep(0.1)

    # The saved filelist can either be retrieved from the subscription callback or
    # via the get_filelist function
    get_filelist()
