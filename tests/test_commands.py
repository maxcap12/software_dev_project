import pytest

from core.board import Orientation
from core.commands import (
    FireCommand,
    PlaceShipCommand,
    ReadyCommand,
    UnknownCommandError,
    parse_command,
)
from core.game import Game
from core.states import InvalidActionError

FLEET = ["Carrier", "Battleship", "Cruiser", "Submarine", "Destroyer"]


def _place_full_fleet(game, player_id):
    for row, ship_name in enumerate(FLEET):
        PlaceShipCommand(ship_name, x=0, y=row, orientation=Orientation.HORIZONTAL).execute(game, player_id)


def _connected_game():
    game = Game()
    game.player_connected(1)
    game.player_connected(2)
    return game


def test_parse_command_builds_ready_command():
    assert isinstance(parse_command({"type": "READY"}), ReadyCommand)


def test_parse_command_builds_place_ship_command():
    command = parse_command(
        {"type": "PLACE_SHIP", "ship": "Destroyer", "x": 0, "y": 0, "orientation": "HORIZONTAL"}
    )
    assert isinstance(command, PlaceShipCommand)
    assert command.orientation == Orientation.HORIZONTAL


def test_parse_command_builds_fire_command():
    command = parse_command({"type": "FIRE", "x": 3, "y": 4})
    assert isinstance(command, FireCommand)
    assert (command.x, command.y) == (3, 4)


def test_parse_command_rejects_unknown_type():
    with pytest.raises(UnknownCommandError):
        parse_command({"type": "NUKE"})


def test_place_ship_command_is_private_to_the_placing_player():
    assert PlaceShipCommand.public is False


def test_place_ship_command_places_ship_on_the_players_board():
    game = _connected_game()

    PlaceShipCommand("Destroyer", x=0, y=0, orientation=Orientation.HORIZONTAL).execute(game, player_id=1)

    assert game.boards[1].cells[0][0].name == "SHIP"
    assert "Destroyer" not in game.fleets[1]


def test_ready_command_requires_full_fleet_placed():
    game = _connected_game()

    with pytest.raises(InvalidActionError):
        ReadyCommand().execute(game, player_id=1)


def test_ready_command_confirms_placement_once_fleet_is_placed():
    game = _connected_game()
    _place_full_fleet(game, 1)
    _place_full_fleet(game, 2)

    ReadyCommand().execute(game, player_id=1)
    assert game.phase_name == "PLACING_SHIPS"

    ReadyCommand().execute(game, player_id=2)
    assert game.phase_name == "PLAYER_1_TURN"


def test_fire_command_resolves_a_hit_and_advances_the_turn():
    game = _connected_game()
    _place_full_fleet(game, 1)
    _place_full_fleet(game, 2)
    ReadyCommand().execute(game, player_id=1)
    ReadyCommand().execute(game, player_id=2)

    result = FireCommand(x=0, y=0).execute(game, player_id=1)

    assert result["hit"] is True
    assert result["ship"] == "Carrier"
    assert game.phase_name == "PLAYER_2_TURN"


def test_fire_command_rejects_out_of_turn_attack():
    game = _connected_game()
    _place_full_fleet(game, 1)
    _place_full_fleet(game, 2)
    ReadyCommand().execute(game, player_id=1)
    ReadyCommand().execute(game, player_id=2)

    with pytest.raises(InvalidActionError):
        FireCommand(x=0, y=0).execute(game, player_id=2)
