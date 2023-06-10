import aiohttp


BASE_URL = "https://www.immobiliare.it/"
SELL_RENT_URL = "{sell_rent}-case/"
CITY_URL = "{city}/"
PAGE_URL = "?pag={page}"


def build_url(is_rent: bool, city: str, page: int) -> str:
    url = BASE_URL
    url += SELL_RENT_URL.format(sell_rent="affitto" if is_rent else "vendita")
    url += CITY_URL.format(city=city)
    url += PAGE_URL.format(page=page)
    return url


async def fetch(url):
    print(f'Fetching {url}')
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url) as response:
            print(f'Got response from {url}')
            return await response.text()
