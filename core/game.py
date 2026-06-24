from core.states import GameOverState, WaitingForPlayersState


class Game:
    def __init__(self):
        self.state = WaitingForPlayersState()
        self.connected_players = set()
        self.ready_players = set()
        self.winner = None

    def transition_to(self, new_state):
        print(f"Game state: {self.state.name} -> {new_state.name}")
        self.state = new_state

    def player_connected(self, player_id):
        self.state.player_connected(self, player_id)

    def confirm_placement(self, player_id):
        self.state.confirm_placement(self, player_id)

    def attack(self, attacker_id):
        self.state.attack(self, attacker_id)

    def end_game(self, winner_id):
        self.winner = winner_id
        self.transition_to(GameOverState())

    @property
    def phase_name(self):
        return self.state.name

    @property
    def current_player(self):
        return getattr(self.state, "player_id", None)
