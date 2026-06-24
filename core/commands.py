from abc import ABC, abstractmethod


class UnknownCommandError(Exception):
    """Raised when a message's "type" doesn't match a known command."""


class Command(ABC):
    type = None

    @abstractmethod
    def execute(self, game, player_id):
        ...


class ReadyCommand(Command):
    type = "READY"

    def execute(self, game, player_id):
        game.confirm_placement(player_id)


class FireCommand(Command):
    type = "FIRE"

    def execute(self, game, player_id):
        game.attack(player_id)


_COMMAND_TYPES = {cls.type: cls for cls in (ReadyCommand, FireCommand)}


def parse_command(data):
    command_cls = _COMMAND_TYPES.get(data.get("type"))
    if command_cls is None:
        raise UnknownCommandError(f"Unknown command type: {data.get('type')!r}")
    return command_cls()
