import json
import socket
import threading

from protocol import receive_lines, send_message

HOST = "127.0.0.1"
PORT = 5000


def receive_loop(sock):
    for line in receive_lines(sock):
        print(f"\n[server] {json.loads(line)}")


def parse_input(raw):
    parts = raw.split()
    if not parts:
        return None

    action = parts[0].lower()
    if action == "ready" and len(parts) == 1:
        return {"type": "READY"}
    if action == "place" and len(parts) == 5:
        _, ship, x, y, orientation = parts
        orientation_name = "HORIZONTAL" if orientation.upper().startswith("H") else "VERTICAL"
        return {"type": "PLACE_SHIP", "ship": ship, "x": int(x), "y": int(y), "orientation": orientation_name}
    if action == "fire" and len(parts) == 3:
        _, x, y = parts
        return {"type": "FIRE", "x": int(x), "y": int(y)}
    return None


def main():
    with socket.create_connection((HOST, PORT)) as sock:
        print(f"Connected to server at {HOST}:{PORT}")

        listener = threading.Thread(target=receive_loop, args=(sock,), daemon=True)
        listener.start()

        print("Commands: 'place <Ship> <x> <y> <H|V>', 'ready', 'fire <x> <y>'")
        while True:
            try:
                raw = input("> ").strip()
            except EOFError:
                break

            if raw.lower() in ("quit", "exit"):
                break

            message = parse_input(raw)
            if message is None:
                print("Unknown command.")
                continue

            send_message(sock, message)


if __name__ == "__main__":
    main()
