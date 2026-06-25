from abc import ABC, abstractmethod

from core.board import Orientation


class UnknownCommandError(Exception):
    """Raised when a message's "type" doesn't match a known command."""


class Command(ABC):
    type = None
    public = True

    @classmethod
    def from_data(cls, data):
        return cls()

    @abstractmethod
    def execute(self, game, player_id):
        ...


class ReadyCommand(Command):
    type = "READY"

    def execute(self, game, player_id):
        game.confirm_placement(player_id)
        return {}


class PlaceShipCommand(Command):
    type = "PLACE_SHIP"
    public = False

    def __init__(self, ship_name, x, y, orientation):
        self.ship_name = ship_name
        self.x = x
        self.y = y
        self.orientation = orientation

    @classmethod
    def from_data(cls, data):
        return cls(
            ship_name=data["ship"],
            x=data["x"],
            y=data["y"],
            orientation=Orientation(data["orientation"]),
        )

    def execute(self, game, player_id):
        game.place_ship(player_id, self.ship_name, self.x, self.y, self.orientation)
        return {"ship": self.ship_name}


class FireCommand(Command):
    type = "FIRE"

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def from_data(cls, data):
        return cls(x=data["x"], y=data["y"])

    def execute(self, game, player_id):
        result = game.attack(player_id, self.x, self.y)
        return {"x": self.x, "y": self.y, "attacker": player_id, **result}


_COMMAND_TYPES = {cls.type: cls for cls in (ReadyCommand, PlaceShipCommand, FireCommand)}


def parse_command(data):
    command_cls = _COMMAND_TYPES.get(data.get("type"))
    if command_cls is None:
        raise UnknownCommandError(f"Unknown command type: {data.get('type')!r}")
    return command_cls.from_data(data)
