from clanker_bench.game.model.card import Suit
from clanker_bench.game.model.gamestate import GameState

_LEGAL_SUITS: set[Suit] = {Suit.RED, Suit.BLUE, Suit.GREEN, Suit.YELLOW}

def is_legal_trump_select(state: GameState, suit: Suit) -> bool:
    if not state.round_state.awaiting_trump_select:
        return False
    elif suit not in _LEGAL_SUITS:
        return False
    return True

def legal_trump_selects(state: GameState) -> set[Suit]:
    if not state.round_state.awaiting_trump_select:
        return set()
    else:
        return _LEGAL_SUITS.copy()