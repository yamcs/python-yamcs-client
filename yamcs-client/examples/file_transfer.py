import io
import time

from yamcs.client import YamcsClient

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

    # Transfer myfile from bucket to spacecraft
    upload = service.upload(out_bucket.name, "myfile", "/CF:/mytarget")
    upload.await_complete(timeout=10)

    if not upload.is_success():
        print("Upload failure:", upload.error)
    else:
        print(f"Successfully uploaded {upload.remote_path} ({upload.size} bytes)")

    # Transfer myfile, but use an alternative destination entity
    upload = service.upload(
        out_bucket.name, "myfile", "/CF:/mytarget", destination_entity="target2",
    )
    upload.await_complete(timeout=10)

    if not upload.is_success():
        print("Upload failure:", upload.error)
    else:
        print(f"Successfully uploaded {upload.remote_path} ({upload.size} bytes)")

    # Download todownload from the remote
    download = service.download(in_bucket.name, "todownload")
    download.await_complete(timeout=10)

    if not download.is_success():
        print("Download failure:", download.error)
    else:
        print(f"Successfully downloaded {download.remote_path} ({download.size} bytes)")

    # DIRECTORY LISTING
    updated = False

    def update(filelist):
        global updated
        updated = True
        print(f"Filelist updated with {len(filelist.files)} files or directories")

    subscription = service.create_filelist_subscription(on_data=update)
    filelist_request = service.fetch_filelist("/")

    start = time.time()
    while not updated and time.time() - start < 20:
        time.sleep(0.1)

    # The saved filelist can either be retrieved from the subscription callback or
    # via the get_filelist function
    filelist_response = service.get_filelist("/")
    if filelist_response:
        print("File list received:")
        if not filelist_response.files:
            print("\tEmpty file list")
        for file in filelist_response.files:
            print(f"\t{file.name + ('/' if file.isDirectory else ''):<12}\
            t{str(file.size) + ' bytes':>12}\tLast Modified: {file.modified.seconds}")
    else:
        print("No filelist found")
