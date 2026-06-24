import socket
import threading

import client


def test_receive_loop_prints_messages_from_server(capsys):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 0))
    server_socket.listen()
    port = server_socket.getsockname()[1]

    def run_server():
        conn, _ = server_socket.accept()
        conn.sendall(b'{"type": "WELCOME", "player_id": 1}\n')
        conn.close()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    with socket.create_connection(("127.0.0.1", port)) as client_sock:
        client.receive_loop(client_sock)

    server_thread.join(timeout=2)
    server_socket.close()

    captured = capsys.readouterr()
    assert "WELCOME" in captured.out
    assert "player_id" in captured.out
