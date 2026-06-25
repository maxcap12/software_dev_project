import json
import socket
import threading

import server as server_module
from core.game import Game


def _read_message(sock):
    data = b""
    while not data.endswith(b"\n"):
        data += sock.recv(1)
    return json.loads(data.decode())


def _place_fleet(sock):
    fleet = ["Carrier", "Battleship", "Cruiser", "Submarine", "Destroyer"]
    for row, name in enumerate(fleet):
        message = {"type": "PLACE_SHIP", "ship": name, "x": 0, "y": row, "orientation": "HORIZONTAL"}
        sock.sendall((json.dumps(message) + "\n").encode())
        _read_message(sock)


def test_full_handshake_and_turn_flow_over_real_sockets():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 0))
    server_socket.listen()
    port = server_socket.getsockname()[1]

    game = Game()

    def run_server():
        connections = server_module.wait_for_players(server_socket, game)
        server_module.run_game_loop(connections, game)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    p1 = socket.create_connection(("127.0.0.1", port))
    assert _read_message(p1) == {"type": "WELCOME", "player_id": 1}

    p2 = socket.create_connection(("127.0.0.1", port))
    assert _read_message(p2) == {"type": "WELCOME", "player_id": 2}

    assert _read_message(p1) == {"type": "STATE", "phase": "PLACING_SHIPS"}
    assert _read_message(p2) == {"type": "STATE", "phase": "PLACING_SHIPS"}

    # placement results are private: each player only hears about their own ships
    _place_fleet(p1)
    _place_fleet(p2)

    p1.sendall(b'{"type": "READY"}\n')
    assert _read_message(p1) == {"type": "STATE", "phase": "PLACING_SHIPS"}
    assert _read_message(p2) == {"type": "STATE", "phase": "PLACING_SHIPS"}

    p2.sendall(b'{"type": "READY"}\n')
    assert _read_message(p1) == {"type": "STATE", "phase": "PLAYER_1_TURN"}
    assert _read_message(p2) == {"type": "STATE", "phase": "PLAYER_1_TURN"}

    p2.sendall(b'{"type": "FIRE", "x": 9, "y": 9}\n')
    assert _read_message(p2) == {"type": "ERROR", "message": "It is not Player 2's turn"}

    p1.sendall(b'{"type": "FIRE", "x": 0, "y": 0}\n')
    expected = {
        "type": "STATE",
        "phase": "PLAYER_2_TURN",
        "x": 0,
        "y": 0,
        "attacker": 1,
        "hit": True,
        "sunk": False,
        "ship": "Carrier",
    }
    assert _read_message(p1) == expected
    assert _read_message(p2) == expected

    p1.close()
    p2.close()
    server_socket.close()
