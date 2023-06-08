from enum import Enum


class SellOrRent(Enum):
    SELL = "vendita"
    RENT = "affitto"


class Criteria(Enum):
    RELEVANCE = "rilevanza"
    PRICE = "prezzo"
    DATE = "data"
    AREA = "superficie"
    ROOMS = "locali"
    LAST_UPDATE = "dataModifica"


class Order(Enum):
    ASC = "asc"
    DESC = "desc"


BASE_URL = "https://www.immobiliare.it/"
SELL_RENT_URL = "{sell_rent}-case/"
CITY_URL = "{city}/"
ZONE_URL = "{zone}/"
CRITERIA_URL = "?criterio={criteria}&ordine={order}&pag={page}"


def build_url(sell_or_rent: SellOrRent, city: str, order: Order, page: int, criteria: Criteria, zone: str = ''):
    url = BASE_URL
    url += SELL_RENT_URL.format(sell_rent=sell_or_rent.value)
    url += CITY_URL.format(city=city)
    if zone != '':
        url += ZONE_URL.format(zone=zone)
    url += CRITERIA_URL.format(order=order.value, page=page, criteria=criteria.value)
    return url
