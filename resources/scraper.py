import pandas as pd
from bs4 import BeautifulSoup
import requests
from url_handler.url_builder import SellOrRent, Criteria, Order, build_url
from models.house import House
import asyncio
import aiohttp


async def fetch(url):
    print(f'Fetching {url}')
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url) as response:
            print(f'Got response from {url}')
            return await response.text()


async def extract_maximum_page(sell_or_rent: SellOrRent, city: str, zone: str = '') -> int:
    url = build_url(sell_or_rent=sell_or_rent, city=city, criteria=Criteria.LAST_UPDATE, page=1, order=Order.DESC, zone=zone)
    raw_response = await fetch(url)
    soup = BeautifulSoup(raw_response, 'html.parser')
    divs = soup.findAll("div", class_="in-pagination__item is-mobileHidden in-pagination__item--disabled")
    for div in divs:
        # check if div.text is a number
        if div.text.isnumeric():
            return int(div.text)
    return 1


async def extract(sell_or_rent: SellOrRent, city: str, zone: str = '') -> list[str]:
    maximum_page: int = await extract_maximum_page(sell_or_rent, city, zone)
    print("Maximum page: " + str(maximum_page))
    urls = [build_url(sell_or_rent=sell_or_rent, city=city, criteria=Criteria.LAST_UPDATE, page=i, order=Order.DESC, zone=zone) for i in range(1, maximum_page + 1)]
    tasks = [asyncio.create_task(fetch(url)) for url in urls]
    raw_results = await asyncio.gather(*tasks)
    return raw_results


async def map_houses(raw_result: str) -> list[House]:
    soup = BeautifulSoup(raw_result, 'html.parser')
    raw_list = soup.find("ul", class_="nd-list in-realEstateResults").find_all("li", class_="nd-list__item in-realEstateResults__item", recursive=False)

    def process_single_li_element(li) -> House:
        anchor = li.find("a", class_="in-card__title")
        property_id = int(anchor["href"].rstrip("/").split("/")[-1])
        title = anchor.text
        price = li.find("li", class_="nd-list__item in-feat__item in-feat__item--main in-realEstateListCard__features--main")
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
            id=property_id,
            title=title,
            price=price,
            surface=surface,
            rooms=rooms,
            bathrooms=bathrooms,
            floor=floor
        )

    processed_list = map(process_single_li_element, raw_list)
    return list(processed_list)


async def scrape(sell_or_rent: SellOrRent, city: str, zone: str = '') -> pd.DataFrame:
    raw_results = await extract(sell_or_rent, city, zone)
    tasks = [asyncio.create_task(map_houses(raw_result)) for raw_result in raw_results]
    houses = await asyncio.gather(*tasks)
    houses = [house for sublist in houses for house in sublist]
    df = pd.DataFrame(houses)
    return df
