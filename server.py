import json
import socket
import threading

from core.board import AttackError, PlacementError
from core.commands import UnknownCommandError, parse_command
from core.game import Game
from core.states import InvalidActionError
from protocol import receive_lines, send_message

HOST = "0.0.0.0"
PORT = 5000


def wait_for_players(server_socket, game):
    players = []

    while len(players) < 2:
        conn, addr = server_socket.accept()
        player_id = len(players) + 1
        print(f"Player {player_id} connected from {addr}")
        send_message(conn, {"type": "WELCOME", "player_id": player_id})
        players.append(conn)
        game.player_connected(player_id)

    return players


def handle_player(conn, player_id, game, connections, lock):
    for line in receive_lines(conn):
        try:
            command = parse_command(json.loads(line))
        except (UnknownCommandError, KeyError, ValueError) as exc:
            send_message(conn, {"type": "ERROR", "message": str(exc)})
            continue

        with lock:
            try:
                details = command.execute(game, player_id)
            except (InvalidActionError, AttackError, PlacementError) as exc:
                send_message(conn, {"type": "ERROR", "message": str(exc)})
                continue
            message = {"type": "STATE", "phase": game.phase_name, **details}
            if game.winner is not None:
                message["winner"] = game.winner

        recipients = connections if command.public else [conn]
        for recipient in recipients:
            send_message(recipient, message)


def run_game_loop(connections, game):
    for conn in connections:
        send_message(conn, {"type": "STATE", "phase": game.phase_name})

    lock = threading.Lock()
    threads = [
        threading.Thread(target=handle_player, args=(conn, player_id, game, connections, lock))
        for player_id, conn in enumerate(connections, start=1)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}, waiting for 2 players...")

    game = Game()
    connections = wait_for_players(server_socket, game)
    print(f"Both players connected. Game phase: {game.phase_name}")

    run_game_loop(connections, game)


if __name__ == "__main__":
    main()
