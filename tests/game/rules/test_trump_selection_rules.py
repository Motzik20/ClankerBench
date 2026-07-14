"""Tests for trump selection.

Rule: Wird ein SINGULARITY aufgedeckt, bestimmt der ausgebende Spieler die
Trumpffarbe, nachdem er seine Handkarten angeschaut hat. Es kann nur eine der
vier echten Farben (RED/BLUE/GREEN/YELLOW) als Trumpf gewaehlt werden.
"""
import pytest

from clanker_bench.game.model.card import Suit
from clanker_bench.game.model.gamestate import Phase
from clanker_bench.game.rules.trump_selection_rules import (
    is_legal_trump_select,
    legal_trump_selects,
)
from tests.game.conftest import make_state

COLOURS = {Suit.RED, Suit.BLUE, Suit.GREEN, Suit.YELLOW}


class TestIsLegalTrumpSelect:
    @pytest.mark.parametrize("suit", sorted(COLOURS, key=lambda s: s.value))
    def test_colours_legal_when_awaiting(self, suit):
        assert is_legal_trump_select(make_state(phase=Phase.SELECT_TRUMP), suit)

    @pytest.mark.parametrize("suit", [Suit.CLANKER, Suit.SINGULARITY])
    def test_clanker_and_singularity_never_legal(self, suit):
        assert not is_legal_trump_select(make_state(phase=Phase.SELECT_TRUMP), suit)

    @pytest.mark.parametrize("suit", list(Suit))
    def test_nothing_legal_when_not_awaiting(self, suit):
        assert not is_legal_trump_select(make_state(phase=Phase.PREDICT), suit)


class TestLegalTrumpSelects:
    def test_returns_four_colours_when_awaiting(self):
        assert legal_trump_selects(Phase.SELECT_TRUMP) == COLOURS

    def test_empty_when_not_awaiting(self):
        assert legal_trump_selects(Phase.PREDICT) == set()
