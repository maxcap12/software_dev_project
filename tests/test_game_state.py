import pytest

from core.game import Game
from core.states import InvalidActionError


def _ready_game():
    game = Game()
    game.player_connected(1)
    game.player_connected(2)
    game.confirm_placement(1)
    game.confirm_placement(2)
    return game


def test_starts_in_waiting_for_players():
    game = Game()
    assert game.phase_name == "WAITING_FOR_PLAYERS"


def test_transitions_to_placing_ships_once_both_connected():
    game = Game()
    game.player_connected(1)
    assert game.phase_name == "WAITING_FOR_PLAYERS"

    game.player_connected(2)
    assert game.phase_name == "PLACING_SHIPS"


def test_transitions_to_player_1_turn_once_both_ready():
    game = Game()
    game.player_connected(1)
    game.player_connected(2)

    game.confirm_placement(1)
    assert game.phase_name == "PLACING_SHIPS"

    game.confirm_placement(2)
    assert game.phase_name == "PLAYER_1_TURN"


def test_turns_alternate_after_each_attack():
    game = _ready_game()
    assert game.phase_name == "PLAYER_1_TURN"

    game.attack(1)
    assert game.phase_name == "PLAYER_2_TURN"

    game.attack(2)
    assert game.phase_name == "PLAYER_1_TURN"


def test_attack_out_of_turn_is_rejected():
    game = _ready_game()
    with pytest.raises(InvalidActionError):
        game.attack(2)
    assert game.phase_name == "PLAYER_1_TURN"


def test_cannot_attack_before_placement_is_done():
    game = Game()
    game.player_connected(1)
    game.player_connected(2)
    with pytest.raises(InvalidActionError):
        game.attack(1)


def test_end_game_moves_to_game_over_and_blocks_further_attacks():
    game = _ready_game()
    game.end_game(winner_id=1)

    assert game.phase_name == "GAME_OVER"
    assert game.winner == 1
    with pytest.raises(InvalidActionError):
        game.attack(2)
