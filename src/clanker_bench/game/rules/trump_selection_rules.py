from clanker_bench.game.model.card import Suit
from clanker_bench.game.model.gamestate import GameState, Phase

_LEGAL_SUITS: set[Suit] = {Suit.RED, Suit.BLUE, Suit.GREEN, Suit.YELLOW}


def is_legal_trump_select(state: GameState, suit: Suit) -> bool:
    return suit in legal_trump_selects(state.phase)


def legal_trump_selects(phase: Phase) -> set[Suit]:
    if phase != Phase.SELECT_TRUMP:
        return set()
    return _LEGAL_SUITS.copy()
