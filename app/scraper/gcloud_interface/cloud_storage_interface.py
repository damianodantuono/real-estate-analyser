# create an interface with GCP Cloud Storage
from google.cloud import storage


class GCSInterface:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_from_path(self, source_file_name: str, destination_blob_name: str):
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"File {source_file_name} uploaded to {destination_blob_name}.")

    def upload_from_bytes(self, string: bytes, destination_blob_name: str):
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_string(string)
        print(f"String uploaded to {destination_blob_name}.")
