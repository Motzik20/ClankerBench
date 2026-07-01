"""Tests for trump selection.

Rule: Wird ein SINGULARITY aufgedeckt, bestimmt der ausgebende Spieler die
Trumpffarbe, nachdem er seine Handkarten angeschaut hat. Es kann nur eine der
vier echten Farben (RED/BLUE/GREEN/YELLOW) als Trumpf gewaehlt werden.
"""
import pytest

from clanker_bench.game.model.card import Suit
from clanker_bench.game.model.gamestate import GameState, RoundState, TrickState, Phase
from clanker_bench.game.model.scoreboard import Scoreboard
from clanker_bench.game.rules.trump_selection_rules import (
    is_legal_trump_select,
    legal_trump_selects,
)

COLOURS = {Suit.RED, Suit.BLUE, Suit.GREEN, Suit.YELLOW}


def make_state(awaiting_trump_select: bool) -> GameState:
    return GameState(
        round_nr=1,
        round_count=10,
        dealer_id=0,
        player_count=3,
        scoreboard=Scoreboard(),
        players=[],
        phase= Phase.SELECT_TRUMP if awaiting_trump_select else Phase.PREDICT,
        round_state=RoundState(
            current_trump_suit=None,
        ),
        trick_state=TrickState(starting_player=0, current_player=0),
    )


class TestIsLegalTrumpSelect:
    @pytest.mark.parametrize("suit", sorted(COLOURS, key=lambda s: s.value))
    def test_colours_legal_when_awaiting(self, suit):
        assert is_legal_trump_select(make_state(awaiting_trump_select=True), suit)

    @pytest.mark.parametrize("suit", [Suit.CLANKER, Suit.SINGULARITY])
    def test_clanker_and_singularity_never_legal(self, suit):
        assert not is_legal_trump_select(make_state(awaiting_trump_select=True), suit)

    @pytest.mark.parametrize("suit", list(Suit))
    def test_nothing_legal_when_not_awaiting(self, suit):
        assert not is_legal_trump_select(make_state(awaiting_trump_select=False), suit)


class TestLegalTrumpSelects:
    def test_returns_four_colours_when_awaiting(self):
        assert legal_trump_selects(make_state(awaiting_trump_select=True)) == COLOURS

    def test_empty_when_not_awaiting(self):
        assert legal_trump_selects(make_state(awaiting_trump_select=False)) == set()
