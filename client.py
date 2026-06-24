import json
import socket
import threading

from protocol import receive_lines, send_message

HOST = "127.0.0.1"
PORT = 5000


def receive_loop(sock):
    for line in receive_lines(sock):
        print(f"\n[server] {json.loads(line)}")


def main():
    with socket.create_connection((HOST, PORT)) as sock:
        print(f"Connected to server at {HOST}:{PORT}")

        listener = threading.Thread(target=receive_loop, args=(sock,), daemon=True)
        listener.start()

        print("Type 'ready' once your ships are placed, or 'fire' to attack on your turn.")
        while True:
            try:
                command = input("> ").strip().lower()
            except EOFError:
                break

            if command == "ready":
                send_message(sock, {"type": "READY"})
            elif command == "fire":
                send_message(sock, {"type": "FIRE"})
            elif command in ("quit", "exit"):
                break
            else:
                print("Unknown command. Type 'ready' or 'fire'.")


if __name__ == "__main__":
    main()
