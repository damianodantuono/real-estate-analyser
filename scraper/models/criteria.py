from enum import Enum


class Criteria(Enum):
    RELEVANCE = "rilevanza"
    PRICE = "prezzo"
    DATE = "data"
    AREA = "superficie"
    ROOMS = "locali"
    LAST_UPDATE = "dataModifica"
