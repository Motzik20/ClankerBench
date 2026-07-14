from clanker_bench.game.model.gamestate import GameState


def is_legal_trick_prediction(state: GameState, predicted_tricks: int) -> bool:
    return predicted_tricks in legal_trick_predictions(
        state.round_nr,
        state.round_state.predicted_player_tricks,
        state.round_state.dealer_id,
        state.trick_state.current_player,
    )


def tricks_in_round(round_nr: int) -> int:
    """Round 0 deals 1 card → 1 trick; round r → r+1 tricks."""
    return round_nr + 1


def legal_trick_predictions(
    round_nr: int, players_predicted_tricks: list[int], dealer_id: int, player_id: int,
) -> list[int]:
    num_tricks = tricks_in_round(round_nr)
    candidates = range(0, num_tricks + 1)  # 0..num_tricks inclusive
    if dealer_id == player_id:
        current_sum = sum(t for t in players_predicted_tricks if t != -1)
        forbidden = num_tricks - current_sum
        return [i for i in candidates if i != forbidden]
    return list(candidates)
