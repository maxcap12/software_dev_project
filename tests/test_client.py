import socket
import threading

import client


def test_client_prints_messages_from_server(monkeypatch, capsys):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 0))
    server_socket.listen()
    port = server_socket.getsockname()[1]

    def run_server():
        conn, _ = server_socket.accept()
        conn.sendall(b"Welcome, you are Player 1\n")
        conn.close()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    monkeypatch.setattr(client, "PORT", port)
    client.main()

    server_thread.join(timeout=2)
    server_socket.close()

    captured = capsys.readouterr()
    assert "Welcome, you are Player 1" in captured.out
    assert "Server closed the connection." in captured.out
