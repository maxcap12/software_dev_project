import json
import socket
import threading

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Input, RichLog, Static

from client import parse_input
from protocol import receive_lines, send_message

HOST = "127.0.0.1"
PORT = 5000

SHIP_SIZES = {
    "Carrier": 5,
    "Battleship": 4,
    "Cruiser": 3,
    "Submarine": 3,
    "Destroyer": 2,
}
TOTAL_SHIPS = len(SHIP_SIZES)


def _empty_row() -> list[Text]:
    return [Text(".", style="bright_black") for _ in range(10)]


class GameOverScreen(ModalScreen):
    BINDINGS = [("q", "quit_app", "Quit"), ("escape", "quit_app", "Quit")]

    CSS = """
    GameOverScreen {
        align: center middle;
    }

    #game-over-box {
        width: auto;
        min-width: 36;
        height: auto;
        padding: 2 4;
        border: double $accent;
        background: $surface;
    }

    #game-over-msg {
        text-align: center;
        width: 100%;
    }

    #game-over-hint {
        text-align: center;
        width: 100%;
        color: $text-muted;
    }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="game-over-box"):
            yield Static(self._message, id="game-over-msg")
            yield Static("Press Q to quit", id="game-over-hint")

    def action_quit_app(self) -> None:
        self.app.exit()


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
        self._fleet_grid = [[False] * 10 for _ in range(10)]
        self._pending_placements: dict[str, dict] = {}
        self._ships_placed = 0
        self._phase: str | None = None
        self._player_id: int | None = None
        self._ready_sent: bool = False
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
                self.call_from_thread(self._handle_server_message, msg)
        except Exception as exc:
            self.call_from_thread(self._write, f"[red]Connection closed: {exc}[/red]")
            self.call_from_thread(self._set_status, "Disconnected")

    def _handle_server_message(self, msg: dict) -> None:
        msg_type = msg.get("type")

        if msg_type == "ERROR":
            self._ready_sent = False
            self._write(f"[bold red][error][/bold red] {msg.get('message', msg)}")
            return

        if msg_type == "WELCOME":
            self._player_id = msg.get("player_id")
            self._write(f"[bold cyan][server][/bold cyan] {msg}")
            return

        self._write(f"[bold cyan][server][/bold cyan] {msg}")

        if msg_type != "STATE":
            return

        phase = msg.get("phase")
        if phase != self._phase:
            self._phase = phase
            self._ready_sent = False
            if phase == "PLACING_SHIPS":
                self._set_status(f"Placing ships — 0/{TOTAL_SHIPS} placed")
            elif phase in ("PLAYER_1_TURN", "PLAYER_2_TURN"):
                my_turn = phase == f"PLAYER_{self._player_id}_TURN"
                if my_turn:
                    self._set_status("Your turn — fire <x> <y>")
                    self.query_one(Input).disabled = False
                else:
                    self._set_status("Opponent's turn — wait…")
                    self.query_one(Input).disabled = True
        elif phase == "PLACING_SHIPS" and self._ready_sent:
            self._ready_sent = False
            self._set_status("Waiting for opponent to be ready…")

        if "attacker" in msg:
            self._on_fire_result(msg)
        elif "ship" in msg:
            self._on_ship_placed(msg["ship"])

        if "winner" in msg:
            self.query_one(Input).disabled = True
            winner = msg.get("winner")
            if winner == self._player_id:
                self.push_screen(GameOverScreen("[bold green]🎉 You win![/bold green]"))
            else:
                self.push_screen(GameOverScreen("[bold red]💀 You lose.[/bold red]"))

    def _on_ship_placed(self, ship_name: str) -> None:
        pending = self._pending_placements.pop(ship_name, None)
        if pending is None:
            return

        size = SHIP_SIZES.get(ship_name, 0)
        x, y, orientation = pending["x"], pending["y"], pending["orientation"]
        coords = (
            [(x + i, y) for i in range(size)]
            if orientation == "HORIZONTAL"
            else [(x, y + i) for i in range(size)]
        )

        table: DataTable = self.query_one("#fleet-grid", DataTable)
        for cx, cy in coords:
            self._fleet_grid[cy][cx] = True
            table.update_cell(str(cy), str(cx), Text("S", style="bold green"))

        self._ships_placed += 1
        if self._ships_placed == TOTAL_SHIPS:
            self._set_status("All ships placed — type ready when set")
        else:
            self._set_status(f"Placing ships — {self._ships_placed}/{TOTAL_SHIPS} placed")

    def _on_fire_result(self, msg: dict) -> None:
        attacker = msg.get("attacker")
        x, y = msg.get("x"), msg.get("y")
        hit = msg.get("hit")
        sunk = msg.get("sunk")
        ship = msg.get("ship")

        cell = Text("X", style="bold red") if hit else Text("O", style="bold blue")

        if attacker == self._player_id:
            self.query_one("#attack-grid", DataTable).update_cell(str(y), str(x), cell)
            if sunk:
                self._write(f"[red]You sunk their {ship}![/red]")
        else:
            self.query_one("#fleet-grid", DataTable).update_cell(str(y), str(x), cell)
            if sunk:
                self._write(f"[red]Your {ship} was sunk![/red]")

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

        if msg.get("type") == "PLACE_SHIP":
            self._pending_placements[msg["ship"]] = {
                "x": msg["x"],
                "y": msg["y"],
                "orientation": msg["orientation"],
            }

        try:
            send_message(self._sock, msg)
            self._write(f"[dim]> {raw}[/dim]")
            if msg.get("type") == "READY":
                self._ready_sent = True
        except OSError as exc:
            self._write(f"[red]Send failed: {exc}[/red]")
            if msg.get("type") == "PLACE_SHIP":
                self._pending_placements.pop(msg["ship"], None)

    def on_unmount(self) -> None:
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass


if __name__ == "__main__":
    TuiClient().run()
