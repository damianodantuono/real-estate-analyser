import asyncio
import pandas as pd
import numpy as np
from scraper.scraper import scrape
from scraper.gcloud_interface.cloud_storage_interface import GCSInterface
from io import BytesIO
import pendulum
from google.cloud import bigquery


def fetch_cities_to_ingest():
    # Set up BigQuery client
    client = bigquery.Client()

    # Define your project ID, dataset ID, and table ID
    project_id = 'house-scraper-ag'
    dataset_id = 'configuration'
    table_id = 'DTC_TO_INGEST'

    # Construct the table reference
    table_ref = f'{project_id}.{dataset_id}.{table_id}'

    # Define the query to fetch all rows from the table
    query = f'SELECT * FROM `{table_ref}`'

    # Execute the query and fetch the rows
    rows = client.query(query).result()
    rows = [(row[0], row[1], row[2]) for row in rows]
    print(rows)
    return rows


def run_scraper(sell_or_rent: str, city: str, zone: str = '') -> pd.DataFrame:
    data = asyncio.run(scrape(sell_or_rent=sell_or_rent, city=city, zone=zone))
    return data


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    df['price'] = np.where(df['price'] == 'N/A', '-1', df['price'])
    df['price'] = df['price'].replace({'€': '', 'da': '', ',00': '', r'\.': '', 'mese': '', '/': ''}, regex=True).apply(str.split).apply(lambda x: x[0]).astype(int)

    df['surface'] = np.where(df['surface'] == 'N/A', '-1', df['surface'])
    df['surface'] = df['surface'].replace({'m²': '', r'\.': ''}, regex=True).apply(str.split).apply(lambda x: x[0]).astype(int)

    df['rooms'] = np.where(df['rooms'] == 'N/A', '-1', df['rooms'])
    df['rooms'] = df['rooms'].replace({r'\+': ''}, regex=True).apply(str.split).apply(lambda x: x[0]).astype(int)

    df['bathrooms'] = np.where(df['bathrooms'] == 'N/A', '-1', df['bathrooms'])
    df['bathrooms'] = df['bathrooms'].replace({r'\+': ''}, regex=True).apply(str.split).apply(lambda x: x[0]).astype(int)

    df['floor'] = np.where(df['floor'] == 'N/A', '-1', df['floor'])
    df['floor'] = df['floor'].replace({r'T|R|S': '0'}, regex=True).apply(str.split).apply(lambda x: x[0]).astype(int)

    return df


def write_to_gcs(data: pd.DataFrame, city: str, zone: str):
    today = pendulum.today().format("YYYYMMDD")
    buffer = BytesIO()
    data.to_parquet(buffer, engine="pyarrow", index=False, compression="gzip")
    buffer.seek(0)

    gcs_interface = GCSInterface(bucket_name="immobiliare-daily-data")
    destination_blob_name = f"raw_data/{city}/{today}.parquet" if zone == '' else f"raw_data/{city}/{zone}/{today}.parquet"
    gcs_interface.upload_from_bytes(buffer.read(), destination_blob_name=destination_blob_name)
    buffer.close()


def main():
    cities_to_ingest = fetch_cities_to_ingest()
    cities_to_ingest = map(lambda x: (x[0], x[1] if x[1] is not None else '', "affitto" if x[2] else "vendita"), cities_to_ingest)
    for city, zone, sell_or_rent in cities_to_ingest:
        print(f"Running scraper for city: {city}, zone: {zone}, sell/rent: {sell_or_rent}")
        raw_df = run_scraper(sell_or_rent=sell_or_rent, city=city, zone=zone)
        df = process_data(raw_df)
        # write_to_gcs(df, city, zone)
        print(df)


main()
