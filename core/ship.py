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
