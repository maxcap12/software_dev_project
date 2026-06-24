import pytest

from core.commands import FireCommand, ReadyCommand, UnknownCommandError, parse_command
from core.game import Game
from core.states import InvalidActionError


def _connected_game():
    game = Game()
    game.player_connected(1)
    game.player_connected(2)
    return game


def test_parse_command_builds_ready_command():
    assert isinstance(parse_command({"type": "READY"}), ReadyCommand)


def test_parse_command_builds_fire_command():
    assert isinstance(parse_command({"type": "FIRE"}), FireCommand)


def test_parse_command_rejects_unknown_type():
    with pytest.raises(UnknownCommandError):
        parse_command({"type": "NUKE"})


def test_ready_command_confirms_placement_for_the_given_player():
    game = _connected_game()

    ReadyCommand().execute(game, player_id=1)
    assert game.phase_name == "PLACING_SHIPS"

    ReadyCommand().execute(game, player_id=2)
    assert game.phase_name == "PLAYER_1_TURN"


def test_fire_command_advances_the_turn():
    game = _connected_game()
    ReadyCommand().execute(game, player_id=1)
    ReadyCommand().execute(game, player_id=2)

    FireCommand().execute(game, player_id=1)
    assert game.phase_name == "PLAYER_2_TURN"


def test_fire_command_rejects_out_of_turn_attack():
    game = _connected_game()
    ReadyCommand().execute(game, player_id=1)
    ReadyCommand().execute(game, player_id=2)

    with pytest.raises(InvalidActionError):
        FireCommand().execute(game, player_id=2)
