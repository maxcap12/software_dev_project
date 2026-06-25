import pytest

from core.board import Orientation
from core.game import Game
from core.states import InvalidActionError

FLEET = ["Carrier", "Battleship", "Cruiser", "Submarine", "Destroyer"]


def _place_full_fleet(game, player_id):
    for row, ship_name in enumerate(FLEET):
        game.place_ship(player_id, ship_name, x=0, y=row, orientation=Orientation.HORIZONTAL)


def _ready_game():
    game = Game()
    game.player_connected(1)
    game.player_connected(2)
    _place_full_fleet(game, 1)
    _place_full_fleet(game, 2)
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


def test_cannot_confirm_placement_before_fleet_is_fully_placed():
    game = Game()
    game.player_connected(1)
    game.player_connected(2)

    with pytest.raises(InvalidActionError):
        game.confirm_placement(1)


def test_transitions_to_player_1_turn_once_both_ready():
    game = Game()
    game.player_connected(1)
    game.player_connected(2)
    _place_full_fleet(game, 1)
    _place_full_fleet(game, 2)

    game.confirm_placement(1)
    assert game.phase_name == "PLACING_SHIPS"

    game.confirm_placement(2)
    assert game.phase_name == "PLAYER_1_TURN"


def test_turns_alternate_after_each_attack():
    game = _ready_game()
    assert game.phase_name == "PLAYER_1_TURN"

    game.attack(1, 9, 9)
    assert game.phase_name == "PLAYER_2_TURN"

    game.attack(2, 9, 9)
    assert game.phase_name == "PLAYER_1_TURN"


def test_attack_out_of_turn_is_rejected():
    game = _ready_game()
    with pytest.raises(InvalidActionError):
        game.attack(2, 9, 9)
    assert game.phase_name == "PLAYER_1_TURN"


def test_cannot_attack_before_placement_is_done():
    game = Game()
    game.player_connected(1)
    game.player_connected(2)
    with pytest.raises(InvalidActionError):
        game.attack(1, 0, 0)


def test_end_game_moves_to_game_over_and_blocks_further_attacks():
    game = _ready_game()
    game.end_game(winner_id=1)

    assert game.phase_name == "GAME_OVER"
    assert game.winner == 1
    with pytest.raises(InvalidActionError):
        game.attack(2, 9, 9)


def test_sinking_every_ship_ends_the_game():
    game = _ready_game()
    ship_cells = [(x, row) for row, size in enumerate([5, 4, 3, 3, 2]) for x in range(size)]

    for index, (x, y) in enumerate(ship_cells):
        game.attack(1, x, y)
        if index < len(ship_cells) - 1:
            # filler shot into Player 1's empty rows, just to satisfy turn alternation
            game.attack(2, index % 10, 5 + index // 10)

    assert game.phase_name == "GAME_OVER"
    assert game.winner == 1
