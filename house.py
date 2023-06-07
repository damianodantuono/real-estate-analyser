from dataclasses import dataclass, field


@dataclass
class House:
    """
    Property class
    contains name, price, surface, rooms, bathrooms, floor number
    """
    id: int
    title: str
    price: str
    surface: str
    rooms: str
    bathrooms: str
    floor: str
    link: str = field(init=False)

    def __post_init__(self):
        self.id = int(self.id)
        self.link = "https://www.immobiliare.it/annunci/" + str(self.id) + "/"
