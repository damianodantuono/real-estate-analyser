import asyncio
from resources.scraper import scrape
from scraper.gcloud_interface.cloud_storage_interface import GCSInterface
from io import BytesIO
import pendulum


def main(sell_or_rent: str, city: str, zone: str = ''):

    today = pendulum.today().format("YYYYMMDD")
    data = asyncio.run(scrape(sell_or_rent=sell_or_rent, city=city, zone=zone))

    # write to bytes buffer parquet file
    buffer = BytesIO()
    data.to_parquet(buffer, engine="pyarrow", index=False, compression="gzip")
    buffer.seek(0)

    gcs_interface = GCSInterface(bucket_name="immobiliare-daily-data")
    # write bytes buffer to GCS

    destination_blob_name = f"raw_data/{city}/{today}.parquet" if zone == '' else f"raw_data/{city}-{zone}/{today}.parquet"

    gcs_interface.upload_from_bytes(buffer.read(), destination_blob_name=destination_blob_name)
