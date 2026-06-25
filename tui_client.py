import json
import socket
import threading

from textual.app import App, ComposeResult
from textual.widgets import Header, Input, RichLog

from client import parse_input
from protocol import receive_lines, send_message

HOST = "127.0.0.1"
PORT = 5000


class TuiClient(App):
    TITLE = "Battleship"
    SUB_TITLE = f"{HOST}:{PORT}"

    CSS = """
    RichLog {
        height: 1fr;
        padding: 0 1;
    }
    Input {
        dock: bottom;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="log", wrap=True, highlight=True, markup=True)
        yield Input(placeholder="ready | place <Ship> <x> <y> <H|V> | fire <x> <y> | quit")

    def on_mount(self) -> None:
        self._sock = None
        try:
            sock = socket.create_connection((HOST, PORT), timeout=3)
            sock.settimeout(None)
            self._sock = sock
        except (ConnectionRefusedError, OSError) as exc:
            self._write(f"[red]Cannot connect to {HOST}:{PORT} — {exc}[/red]")
            self._write("[dim]Start the server first:  python server.py[/dim]")
            return

        self._write(f"[green]Connected to {HOST}:{PORT}[/green]")
        self._write("[dim]Commands:  ready  |  place <Ship> <x> <y> <H|V>  |  fire <x> <y>  |  quit[/dim]")
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def _receive_loop(self) -> None:
        try:
            for line in receive_lines(self._sock):
                msg = json.loads(line)
                self.call_from_thread(self._write, f"[bold cyan][server][/bold cyan] {msg}")
        except Exception as exc:
            self.call_from_thread(self._write, f"[red]Connection closed: {exc}[/red]")

    def _write(self, text: str) -> None:
        try:
            self.query_one(RichLog).write(text)
        except Exception:
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        event.input.clear()

        if not raw:
            return

        if raw.lower() in ("quit", "exit"):
            self.exit()
            return

        msg = parse_input(raw)
        if msg is None:
            self._write("[yellow]Unknown command. Try: ready | place <Ship> <x> <y> <H|V> | fire <x> <y>[/yellow]")
            return

        if self._sock is None:
            self._write("[red]Not connected — server is unreachable.[/red]")
            return

        try:
            send_message(self._sock, msg)
            self._write(f"[dim]> {raw}[/dim]")
        except OSError as exc:
            self._write(f"[red]Send failed: {exc}[/red]")

    def on_unmount(self) -> None:
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass


if __name__ == "__main__":
    TuiClient().run()
