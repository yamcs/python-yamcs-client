import io

from yamcs.client import YamcsClient

if __name__ == "__main__":
    client = YamcsClient("localhost:8090")
    storage = client.get_storage_client()
    cfdp = client.get_cfdp_client(instance="cfdp")

    # Use pre-existing buckets, one for each direction
    out_bucket = storage.get_bucket("cfdpUp")
    in_bucket = storage.get_bucket("cfdpDown")

    # Prepare a sample file
    file_like = io.StringIO("Sample file content")
    out_bucket.upload_object("myfile", file_like)

    # Transfer myfile from bucket to spacecraft
    upload = cfdp.upload(out_bucket.name, "myfile", "/CF:/mytarget")
    upload.await_complete(timeout=10)

    if not upload.is_success():
        print("Upload failure:", upload.error)
    else:
        print(f"Successfully uploaded {upload.remote_path} ({upload.size} bytes)")
