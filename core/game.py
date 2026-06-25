from core.board import Board
from core.ship import ShipFactory
from core.states import GameOverState, WaitingForPlayersState


class Game:
    def __init__(self):
        self.state = WaitingForPlayersState()
        self.connected_players = set()
        self.ready_players = set()
        self.boards = {1: Board(), 2: Board()}
        self.fleets = {1: ShipFactory.create_fleet(), 2: ShipFactory.create_fleet()}
        self.winner = None

    def transition_to(self, new_state):
        print(f"Game state: {self.state.name} -> {new_state.name}")
        self.state = new_state

    def player_connected(self, player_id):
        self.state.player_connected(self, player_id)

    def place_ship(self, player_id, ship_name, x, y, orientation):
        self.state.place_ship(self, player_id, ship_name, x, y, orientation)

    def confirm_placement(self, player_id):
        self.state.confirm_placement(self, player_id)

    def attack(self, attacker_id, x, y):
        return self.state.attack(self, attacker_id, x, y)

    def end_game(self, winner_id):
        self.winner = winner_id
        self.transition_to(GameOverState())

    @property
    def phase_name(self):
        return self.state.name

    @property
    def current_player(self):
        return getattr(self.state, "player_id", None)
