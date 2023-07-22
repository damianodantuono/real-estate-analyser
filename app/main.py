from module_scraping.scraper import scrape
from gcloud_interface.cloud_storage_interface import GCSInterface
import asyncio
import argparse
from io import BytesIO
import pendulum


if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument("city", type=str)
    parser.add_argument("-r", "--is_rent", action="store_true", default=False)
    parser.add_argument("--bucket", type=str, required=True)
    parser.add_argument("--prefix", type=str, required=False, default="raw_data")
    parser.add_argument("--dry-run", action="store_true", default=False)

    args = parser.parse_args()

    city = args.city
    is_rent = args.is_rent
    bucket = args.bucket
    prefix = args.prefix + '/' + city + '_' + ("rent" if is_rent else "sell") + '_' + pendulum.today().format("YYYYMMDD") + ".parquet.gzip"
    dry_run = args.dry_run

    print(f"Running scraper for {'rent' if is_rent else 'sell'} in {city}")

    df = asyncio.run(scrape(is_rent, city))

    gsi = GCSInterface(bucket)

    stream = BytesIO()
    df.to_parquet(stream, index=False, compression="gzip", engine="pyarrow")
    stream.seek(0)
    file_size = round(stream.getbuffer().nbytes / 1024, 2)

    message = f"{'Would upload' if dry_run else 'Uploaded'} to bucket {bucket} @ location {prefix}.\nFile size: {file_size} KB"

    if not dry_run:
        gsi.upload_from_bytes(stream.read(), prefix)
    else:
        df.to_csv("test.csv", index=False)

    print(message)
