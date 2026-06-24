import json


def send_message(conn, message):
    conn.sendall((json.dumps(message) + "\n").encode())


def receive_lines(conn):
    reader = conn.makefile("r")
    for line in reader:
        line = line.strip()
        if line:
            yield line
