from abc import ABC


class InvalidActionError(Exception):
    """Raised when an action is attempted in a state that doesn't allow it."""


class GameState(ABC):
    name = "BASE_STATE"

    def player_connected(self, game, player_id):
        raise InvalidActionError(f"Cannot connect a player during {self.name}")

    def confirm_placement(self, game, player_id):
        raise InvalidActionError(f"Cannot place ships during {self.name}")

    def attack(self, game, attacker_id):
        raise InvalidActionError(f"Cannot attack during {self.name}")


class WaitingForPlayersState(GameState):
    name = "WAITING_FOR_PLAYERS"

    def player_connected(self, game, player_id):
        game.connected_players.add(player_id)
        if len(game.connected_players) == 2:
            game.transition_to(PlacingShipsState())


class PlacingShipsState(GameState):
    name = "PLACING_SHIPS"

    def confirm_placement(self, game, player_id):
        game.ready_players.add(player_id)
        if len(game.ready_players) == 2:
            game.transition_to(PlayerTurnState(player_id=1))


class PlayerTurnState(GameState):
    def __init__(self, player_id):
        self.player_id = player_id
        self.name = f"PLAYER_{player_id}_TURN"

    def attack(self, game, attacker_id):
        if attacker_id != self.player_id:
            raise InvalidActionError(f"It is not Player {attacker_id}'s turn")
        next_player = 2 if self.player_id == 1 else 1
        game.transition_to(PlayerTurnState(next_player))


class GameOverState(GameState):
    name = "GAME_OVER"
