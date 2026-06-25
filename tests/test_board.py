import pytest

from core.board import AttackError, Board, CellState, Orientation, PlacementError
from core.ship import Ship


def test_place_ship_marks_cells_and_records_coordinates():
    board = Board()
    horizontal_ship = Ship(name="Destroyer", size=2)
    vertical_ship = Ship(name="Submarine", size=3)

    board.place_ship(horizontal_ship, x=0, y=0, orientation=Orientation.HORIZONTAL)
    board.place_ship(vertical_ship, x=3, y=3, orientation=Orientation.VERTICAL)

    assert horizontal_ship.coordinates == [(0, 0), (1, 0)]
    assert board.cells[0][0] == CellState.SHIP
    assert board.cells[0][1] == CellState.SHIP

    assert vertical_ship.coordinates == [(3, 3), (3, 4), (3, 5)]
    assert board.cells[3][3] == CellState.SHIP
    assert board.cells[5][3] == CellState.SHIP


def test_place_ship_rejects_invalid_placement():
    board = Board()

    with pytest.raises(PlacementError):
        board.place_ship(Ship(name="Carrier", size=5), x=8, y=0, orientation=Orientation.HORIZONTAL)

    board.place_ship(Ship(name="Destroyer", size=2), x=0, y=0, orientation=Orientation.HORIZONTAL)
    with pytest.raises(PlacementError):
        board.place_ship(Ship(name="Submarine", size=3), x=1, y=0, orientation=Orientation.VERTICAL)


def test_receive_attack_resolves_miss_hit_and_sunk():
    board = Board()
    ship = Ship(name="Destroyer", size=2)
    board.place_ship(ship, x=0, y=0, orientation=Orientation.HORIZONTAL)

    assert board.receive_attack(5, 5) == {"hit": False, "sunk": False, "ship": None}
    assert board.receive_attack(0, 0) == {"hit": True, "sunk": False, "ship": "Destroyer"}

    assert board.receive_attack(1, 0) == {"hit": True, "sunk": True, "ship": "Destroyer"}
    assert board.all_ships_sunk


def test_receive_attack_rejects_invalid_targets():
    board = Board()
    board.receive_attack(2, 2)

    with pytest.raises(AttackError):
        board.receive_attack(2, 2)

    with pytest.raises(AttackError):
        board.receive_attack(10, 0)
