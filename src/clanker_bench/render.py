from clanker_bench.game.model.card import Card, Suit
from clanker_bench.game.model.gamestate import GameState

_SUIT_CODE = {Suit.RED: "R", Suit.BLUE: "B", Suit.GREEN: "G", Suit.YELLOW: "Y"}


def _card(card: Card) -> str:
    if card.suit == Suit.CLANKER:
        return "CLK"
    if card.suit == Suit.SINGULARITY:
        return "SNG"
    return f"{_SUIT_CODE[card.suit]}{card.rank}"


def render(state: GameState) -> str:
    rs = state.round_state
    ts = state.trick_state
    trump = rs.current_trump_suit.value if rs.current_trump_suit else "none"

    lines = [
        f"=== Round {state.round_nr + 1}/{state.round_count}"
        f" | Trick {rs.trick_nr + 1}"
        f" | Phase {state.phase.value}"
        f" | Trump {trump}"
        f" | Dealer P{rs.dealer_id} ===",
    ]
    for p in state.players:
        pred = rs.predicted_player_tricks[p.player_id]
        pred_str = "-" if pred is None or pred < 0 else str(pred)
        won = rs.actual_player_tricks[p.player_id]
        marker = ">" if p.player_id == ts.current_player else " "
        hand = " ".join(_card(c) for c in p.own_hand) or "-"
        lines.append(
            f" {marker} P{p.player_id} {p.name:<10} pred:{pred_str:>2} won:{won:>2}  hand: [{hand}]",
        )

    trick = (
        "  ".join(f"P{pc.player_id}:{_card(pc.card)}" for pc in ts.current_trick) or "-"
    )
    lines.append(f"   trick: {trick}")
    return "\n".join(lines)
