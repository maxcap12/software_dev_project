from enum import Enum


class CellState(Enum):
    EMPTY = "EMPTY"
    SHIP = "SHIP"
    HIT = "HIT"
    MISS = "MISS"


class Orientation(Enum):
    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"


class PlacementError(Exception):
    """Raised when a ship can't be placed at the requested position."""


class AttackError(Exception):
    """Raised when an attack targets an invalid or already-attacked cell."""


class Board:
    SIZE = 10

    def __init__(self):
        self.cells = [[CellState.EMPTY for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        self.ships = []
        self._ship_at = {}

    def place_ship(self, ship, x, y, orientation):
        coordinates = self._coordinates_for(ship.size, x, y, orientation)

        for cx, cy in coordinates:
            if not self._in_bounds(cx, cy):
                raise PlacementError(f"Ship '{ship.name}' would be out of bounds")
            if (cx, cy) in self._ship_at:
                raise PlacementError(f"Ship '{ship.name}' overlaps another ship")

        ship.coordinates = coordinates
        self.ships.append(ship)
        for cx, cy in coordinates:
            self._ship_at[(cx, cy)] = ship
            self.cells[cy][cx] = CellState.SHIP

    def receive_attack(self, x, y):
        if not self._in_bounds(x, y):
            raise AttackError(f"({x}, {y}) is out of bounds")

        cell = self.cells[y][x]
        if cell in (CellState.HIT, CellState.MISS):
            raise AttackError(f"({x}, {y}) has already been attacked")

        if cell == CellState.SHIP:
            ship = self._ship_at[(x, y)]
            ship.register_hit(x, y)
            self.cells[y][x] = CellState.HIT
            return {"hit": True, "sunk": ship.is_sunk, "ship": ship.name}

        self.cells[y][x] = CellState.MISS
        return {"hit": False, "sunk": False, "ship": None}

    @property
    def all_ships_sunk(self):
        return all(ship.is_sunk for ship in self.ships)

    def _in_bounds(self, x, y):
        return 0 <= x < self.SIZE and 0 <= y < self.SIZE

    def _coordinates_for(self, size, x, y, orientation):
        if orientation == Orientation.HORIZONTAL:
            return [(x + i, y) for i in range(size)]
        return [(x, y + i) for i in range(size)]
