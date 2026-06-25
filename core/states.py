from abc import ABC


class InvalidActionError(Exception):
    """Raised when an action is attempted in a state that doesn't allow it."""


class GameState(ABC):
    name = "BASE_STATE"

    def player_connected(self, game, player_id):
        raise InvalidActionError(f"Cannot connect a player during {self.name}")

    def place_ship(self, game, player_id, ship_name, x, y, orientation):
        raise InvalidActionError(f"Cannot place ships during {self.name}")

    def confirm_placement(self, game, player_id):
        raise InvalidActionError(f"Cannot place ships during {self.name}")

    def attack(self, game, attacker_id, x, y):
        raise InvalidActionError(f"Cannot attack during {self.name}")


class WaitingForPlayersState(GameState):
    name = "WAITING_FOR_PLAYERS"

    def player_connected(self, game, player_id):
        game.connected_players.add(player_id)
        if len(game.connected_players) == 2:
            game.transition_to(PlacingShipsState())


class PlacingShipsState(GameState):
    name = "PLACING_SHIPS"

    def place_ship(self, game, player_id, ship_name, x, y, orientation):
        remaining = game.fleets[player_id]
        if ship_name not in remaining:
            raise InvalidActionError(f"Unknown or already-placed ship: {ship_name!r}")

        game.boards[player_id].place_ship(remaining[ship_name], x, y, orientation)
        del remaining[ship_name]

    def confirm_placement(self, game, player_id):
        if game.fleets[player_id]:
            raise InvalidActionError("Place your entire fleet before confirming ready")

        game.ready_players.add(player_id)
        if len(game.ready_players) == 2:
            game.transition_to(PlayerTurnState(player_id=1))


class PlayerTurnState(GameState):
    def __init__(self, player_id):
        self.player_id = player_id
        self.name = f"PLAYER_{player_id}_TURN"

    def attack(self, game, attacker_id, x, y):
        if attacker_id != self.player_id:
            raise InvalidActionError(f"It is not Player {attacker_id}'s turn")

        defender_id = 2 if attacker_id == 1 else 1
        result = game.boards[defender_id].receive_attack(x, y)

        if game.boards[defender_id].all_ships_sunk:
            game.end_game(winner_id=attacker_id)
        else:
            game.transition_to(PlayerTurnState(defender_id))

        return result


class GameOverState(GameState):
    name = "GAME_OVER"
