def compute_cell(hit: bool) -> tuple[str, str]:
    return ("X", "red") if hit else ("O", "blue")


def status_text(phase: str, player_id: int) -> str:
    if phase in ("PLAYER_1_TURN", "PLAYER_2_TURN"):
        my_turn = phase == f"PLAYER_{player_id}_TURN"
        return "Your turn — fire <x> <y>" if my_turn else "Opponent's turn — wait…"
    if phase == "PLACING_SHIPS":
        return "Placing ships"
    return ""
