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

    p1.sendall(b'{"type": "READY"}\n')
    assert _read_message(p1) == {"type": "STATE", "phase": "PLACING_SHIPS"}
    assert _read_message(p2) == {"type": "STATE", "phase": "PLACING_SHIPS"}

    p2.sendall(b'{"type": "READY"}\n')
    assert _read_message(p1) == {"type": "STATE", "phase": "PLAYER_1_TURN"}
    assert _read_message(p2) == {"type": "STATE", "phase": "PLAYER_1_TURN"}

    p2.sendall(b'{"type": "FIRE"}\n')
    assert _read_message(p2) == {"type": "ERROR", "message": "It is not Player 2's turn"}

    p1.sendall(b'{"type": "FIRE"}\n')
    assert _read_message(p1) == {"type": "STATE", "phase": "PLAYER_2_TURN"}
    assert _read_message(p2) == {"type": "STATE", "phase": "PLAYER_2_TURN"}

    p1.close()
    p2.close()
    server_socket.close()
