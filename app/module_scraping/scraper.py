import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from module_scraping.website_interface import build_url, fetch
from module_scraping.model_house import House
import asyncio
import re

RESULTS_PER_PAGE = 25


def scrape_maximum_page(raw_response: str) -> int:
    soup = BeautifulSoup(raw_response, 'html.parser')
    div = soup.find("div", class_="in-searchList__title")
    if div is None:
        return 1
    text = div.text
    if text is None:
        return 1
    number_of_results = int(re.search(r"\d+", text).group(0))
    return (number_of_results // RESULTS_PER_PAGE) + 1


async def extract_single_page(url: str) -> str:
    raw_response = await fetch(url)
    return raw_response


def map_houses(raw_result: str) -> list[House]:
    soup = BeautifulSoup(raw_result, 'html.parser')
    raw_list = soup \
        .find("ul", {'data-cy': 'result-list'}) \
        .find_all("li", class_="nd-list__item in-realEstateResults__item", recursive=False)

    def process_single_li_element(li) -> House:
        anchor = li.find("a", class_="in-card__title")
        property_id = int(anchor["href"].rstrip("/").split("/")[-1])
        title = anchor.text
        price = li.find("li", class_="in-realEstateListCard__priceOnTop")
        surface = li.find("li", {"aria-label": "superficie"})
        rooms = li.find("li", {"aria-label": "locali"})
        bathrooms = li.find("li", {"aria-label": "bagni"})
        floor = li.find("li", {"aria-label": "piano"})

        price = price.text if price is not None else "N/A"
        surface = surface.text if surface is not None else "N/A"
        rooms = rooms.text if rooms is not None else "N/A"
        bathrooms = bathrooms.text if bathrooms is not None else "N/A"
        floor = floor.text if floor is not None else "N/A"

        return House(
            ID=property_id,
            TITLE=title,
            PRICE=price,
            SURFACE=surface,
            ROOMS=rooms,
            BATHROOMS=bathrooms,
            FLOOR=floor
        )

    processed_list = map(process_single_li_element, raw_list)
    return list(processed_list)


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    df['PRICE'] = np.where(df['PRICE'] == 'N/A', '-1', df['PRICE'])
    df['PRICE'] = df['PRICE'].replace({'€': '', 'da': '', ',00': '', r'\.': '', 'mese': '', '/': ''}, regex=True).apply(
        str.split).apply(lambda x: x[0]).astype(int)

    df['SURFACE'] = np.where(df['SURFACE'] == 'N/A', '-1', df['SURFACE'])
    df['SURFACE'] = df['SURFACE'].replace({'m²': '', r'\.': ''}, regex=True).apply(str.split).apply(
        lambda x: x[0]).astype(int)

    df['ROOMS'] = np.where(df['ROOMS'] == 'N/A', '-1', df['ROOMS'])
    df['ROOMS'] = df['ROOMS'].replace({r'\+': ''}, regex=True).apply(str.split).apply(lambda x: x[0]).astype(int)

    df['BATHROOMS'] = np.where(df['BATHROOMS'] == 'N/A', '-1', df['BATHROOMS'])
    df['BATHROOMS'] = df['BATHROOMS'].replace({r'\+': ''}, regex=True).apply(str.split).apply(lambda x: x[0]).astype(
        int)

    df['FLOOR'] = np.where(df['FLOOR'] == 'N/A', '-1', df['FLOOR'])
    df['FLOOR'] = df['FLOOR'].replace({r'T|R|S': '0'}, regex=True).apply(str.split).apply(lambda x: x[0]).astype(int)

    return df


async def scrape(is_rent: bool, city: str) -> pd.DataFrame:
    # Extracting the first page to get the maximum number of pages
    first_page_raw_html = await extract_single_page(build_url(is_rent, city, 1))
    maximum_page = scrape_maximum_page(first_page_raw_html)
    print("Maximum page: ", maximum_page)

    # Extracting the remaining pages up to the maximum page
    urls = [build_url(is_rent, city, page) for page in range(2, maximum_page + 1)]
    raw_htmls = await asyncio.gather(*map(extract_single_page, urls))
    raw_htmls.insert(0, first_page_raw_html)

    # Extracting houses from raw htmls
    houses = map(map_houses, raw_htmls)
    houses = [house for sublist in houses for house in sublist]
    raw_df = pd.DataFrame(houses)

    # Processing data
    df = process_data(raw_df)
    df['CITY_NAME'] = city
    df['IS_RENT'] = is_rent

    print("Extracted ", len(df), " houses")

    return df
