from client import parse_input
from tui_helpers import compute_cell, status_text


# ── parse_input ────────────────────────────────────────────────────────────────


def test_parse_input_place_horizontal():
    assert parse_input("place Carrier 0 0 H") == {
        "type": "PLACE_SHIP",
        "ship": "Carrier",
        "x": 0,
        "y": 0,
        "orientation": "HORIZONTAL",
    }


def test_parse_input_place_vertical():
    assert parse_input("place Destroyer 3 5 V") == {
        "type": "PLACE_SHIP",
        "ship": "Destroyer",
        "x": 3,
        "y": 5,
        "orientation": "VERTICAL",
    }


def test_parse_input_fire():
    assert parse_input("fire 3 4") == {"type": "FIRE", "x": 3, "y": 4}


def test_parse_input_ready():
    assert parse_input("ready") == {"type": "READY"}


def test_parse_input_garbage_returns_none():
    assert parse_input("garbage input") is None


# ── compute_cell ───────────────────────────────────────────────────────────────


def test_compute_cell_hit():
    assert compute_cell(True) == ("X", "red")


def test_compute_cell_miss():
    assert compute_cell(False) == ("O", "blue")


# ── status_text ────────────────────────────────────────────────────────────────


def test_status_text_player1_turn_own_client():
    assert "Your turn" in status_text("PLAYER_1_TURN", 1)


def test_status_text_player1_turn_other_client():
    assert "Opponent" in status_text("PLAYER_1_TURN", 2)


def test_status_text_player2_turn_own_client():
    assert "Your turn" in status_text("PLAYER_2_TURN", 2)


def test_status_text_placing_ships():
    assert "Placing" in status_text("PLACING_SHIPS", 1)
