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