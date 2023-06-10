from dataclasses import dataclass, field


@dataclass
class House:
    """
    Property class
    contains name, price, surface, rooms, bathrooms, floor number
    """
    ID: int
    TITLE: str
    PRICE: str
    SURFACE: str
    ROOMS: str
    BATHROOMS: str
    FLOOR: str
    LINK: str = field(init=False)

    def __post_init__(self):
        self.ID = int(self.ID)
        self.LINK = "https://www.immobiliare.it/annunci/" + str(self.ID) + "/"
