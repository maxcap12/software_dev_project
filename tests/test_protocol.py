import json
import socket
import threading

from protocol import receive_lines, send_message


def test_send_message_and_receive_lines_round_trip():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 0))
    server_socket.listen()
    port = server_socket.getsockname()[1]

    received = {}

    def run_server():
        conn, _ = server_socket.accept()
        received["lines"] = [json.loads(line) for line in receive_lines(conn)]
        conn.close()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    client_sock = socket.create_connection(("127.0.0.1", port))
    send_message(client_sock, {"type": "FIRE"})
    send_message(client_sock, {"type": "READY"})
    client_sock.close()

    server_thread.join(timeout=2)
    server_socket.close()

    assert received["lines"] == [{"type": "FIRE"}, {"type": "READY"}]
