from scraper.models.criteria import Criteria
from scraper.models.order import Order


BASE_URL = "https://www.immobiliare.it/"
SELL_RENT_URL = "{sell_rent}-case/"
CITY_URL = "{city}/"
ZONE_URL = "{zone}/"
CRITERIA_URL = "?criterio={criteria}&ordine={order}&pag={page}"


def build_url(sell_or_rent: str, city: str, order: Order, page: int, criteria: Criteria, zone: str = ''):
    url = BASE_URL
    url += SELL_RENT_URL.format(sell_rent=sell_or_rent)
    url += CITY_URL.format(city=city)
    if zone != '':
        url += ZONE_URL.format(zone=zone)
    url += CRITERIA_URL.format(order=order.value, page=page, criteria=criteria.value)
    return url
