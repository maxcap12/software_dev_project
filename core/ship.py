class Ship:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.coordinates = []
        self.hits = set()

    def register_hit(self, x, y):
        self.hits.add((x, y))

    @property
    def is_sunk(self):
        return bool(self.coordinates) and set(self.coordinates).issubset(self.hits)


class ShipFactory:
    _SHIP_SIZES = {
        "Carrier": 5,
        "Battleship": 4,
        "Cruiser": 3,
        "Submarine": 3,
        "Destroyer": 2,
    }

    @classmethod
    def create(cls, name):
        return Ship(name=name, size=cls._SHIP_SIZES[name])

    @classmethod
    def create_fleet(cls):
        return {name: cls.create(name) for name in cls._SHIP_SIZES}
