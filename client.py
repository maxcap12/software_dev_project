import socket

HOST = "127.0.0.1"
PORT = 5000


def main():
    with socket.create_connection((HOST, PORT)) as sock:
        print(f"Connected to server at {HOST}:{PORT}")
        while True:
            data = sock.recv(1024)
            if not data:
                print("Server closed the connection.")
                break
            print(data.decode().strip())


if __name__ == "__main__":
    main()
