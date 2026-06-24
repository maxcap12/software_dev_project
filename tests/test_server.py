import json
import socket
import threading

from core.game import Game
from server import wait_for_players


def test_wait_for_players_accepts_two_connections_in_order():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 0))
    server_socket.listen()
    port = server_socket.getsockname()[1]

    game = Game()
    result = {}

    def run_server():
        result["players"] = wait_for_players(server_socket, game)

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    client1 = socket.create_connection(("127.0.0.1", port))
    assert json.loads(client1.recv(1024)) == {"type": "WELCOME", "player_id": 1}

    client2 = socket.create_connection(("127.0.0.1", port))
    assert json.loads(client2.recv(1024)) == {"type": "WELCOME", "player_id": 2}

    server_thread.join(timeout=2)

    assert len(result["players"]) == 2
    assert game.phase_name == "PLACING_SHIPS"

    client1.close()
    client2.close()
    server_socket.close()
