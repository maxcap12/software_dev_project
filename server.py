import socket

HOST = "0.0.0.0"
PORT = 5000


def wait_for_players(server_socket):
    players = []
    
    while len(players) < 2:
        conn, addr = server_socket.accept()
        player_id = len(players) + 1
        print(f"Player {player_id} connected from {addr}")
        conn.sendall(f"Welcome, you are Player {player_id}\n".encode())
        players.append(conn)

    return players


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}, waiting for 2 players...")

    players = wait_for_players(server_socket)
    print("Both players connected. Game can start.")

    for conn in players:
        conn.sendall(b"Both players connected. Game starting!\n")


if __name__ == "__main__":
    main()
