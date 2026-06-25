import json
import socket
import threading

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Header, Input, RichLog, Static

from client import parse_input
from protocol import receive_lines, send_message

HOST = "127.0.0.1"
PORT = 5000


def _empty_row() -> list[Text]:
    return [Text(".", style="bright_black") for _ in range(10)]


class TuiClient(App):
    TITLE = "Battleship"
    SUB_TITLE = f"{HOST}:{PORT}"

    CSS = """
    #body {
        height: 1fr;
    }

    #top-row {
        height: 1fr;
    }

    #fleet-grid, #attack-grid {
        width: 1fr;
        border: solid $accent;
    }

    #bottom-row {
        height: 8;
    }

    #status {
        width: 1fr;
        border: solid $accent;
        padding: 1 2;
    }

    #log {
        width: 1fr;
        border: solid $accent;
    }

    Input {
        dock: bottom;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="body"):
            with Horizontal(id="top-row"):
                yield DataTable(id="fleet-grid")
                yield DataTable(id="attack-grid")
            with Horizontal(id="bottom-row"):
                yield Static("", id="status")
                yield RichLog(id="log", wrap=True, highlight=True, markup=True)
        yield Input(placeholder="ready | place <Ship> <x> <y> <H|V> | fire <x> <y> | quit")

    def on_mount(self) -> None:
        self._sock = None
        self._setup_grids()
        self._connect()

    def _setup_grids(self) -> None:
        for widget_id, title in (("fleet-grid", "YOUR FLEET"), ("attack-grid", "ATTACK GRID")):
            table: DataTable = self.query_one(f"#{widget_id}", DataTable)
            table.border_title = title
            table.cursor_type = "none"
            for col in range(10):
                table.add_column(str(col), key=str(col), width=3)
            for row in range(10):
                table.add_row(*_empty_row(), key=str(row), label=Text(str(row), style="bold"))

        self.query_one("#status", Static).border_title = "Status"
        self.query_one("#log", RichLog).border_title = "Messages"

    def _connect(self) -> None:
        try:
            sock = socket.create_connection((HOST, PORT), timeout=3)
            sock.settimeout(None)
            self._sock = sock
        except (ConnectionRefusedError, OSError) as exc:
            self._write(f"[red]Cannot connect to {HOST}:{PORT} — {exc}[/red]")
            self._write("[dim]Start the server first:  python server.py[/dim]")
            self._set_status("Not connected")
            return

        self._write(f"[green]Connected to {HOST}:{PORT}[/green]")
        self._write("[dim]Commands:  ready  |  place <Ship> <x> <y> <H|V>  |  fire <x> <y>  |  quit[/dim]")
        self._set_status("Connected — waiting for second player…")
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def _receive_loop(self) -> None:
        try:
            for line in receive_lines(self._sock):
                msg = json.loads(line)
                self.call_from_thread(self._write, f"[bold cyan][server][/bold cyan] {msg}")
        except Exception as exc:
            self.call_from_thread(self._write, f"[red]Connection closed: {exc}[/red]")
            self.call_from_thread(self._set_status, "Disconnected")

    def _write(self, text: str) -> None:
        try:
            self.query_one("#log", RichLog).write(text)
        except Exception:
            pass

    def _set_status(self, text: str) -> None:
        try:
            self.query_one("#status", Static).update(text)
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
