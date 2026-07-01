"""Tests for the follow-suit ("Bedienen") rules.

Rule (German original):
  - Ein SINGULARITY oder ein CLANKER kann immer ausgespielt werden.
  - CLANKER am Anfang eines Stiches haben auf das Folgende keinen Einfluss.
  - Ist die erste Karte eines Stiches (nach moeglichen CLANKER) ein SINGULARITY,
    koennen danach beliebige Karten ausgespielt werden.
  - Sonst ist die Farbe der ersten nicht-CLANKER Karte diejenige, welche bedient
    werden muss (das kann auch die Trumpffarbe sein). Wer sie hat, muss sie
    spielen; wer sie nicht hat, darf eine beliebige andere Karte spielen.
"""
import pytest

from clanker_bench.game.model.card import Card, Suit
from clanker_bench.game.model.gamestate import GameState, PlayedCard, RoundState, TrickState, Phase
from clanker_bench.game.model.player_state import PlayerState
from clanker_bench.game.model.scoreboard import Scoreboard
from clanker_bench.game.rules.play_card_rules import (
    compute_demanded_suit,
    get_allowed_suits,
    is_legal_card_play,
)

CLANKER = Card(suit=Suit.CLANKER)
SINGULARITY = Card(suit=Suit.SINGULARITY)


def card(suit: Suit, rank: int = 1) -> Card:
    return Card(suit=suit, rank=rank)


def trick(*cards: Card) -> list[PlayedCard]:
    return [PlayedCard(player_id=i, card=c) for i, c in enumerate(cards)]


def make_state(hand: list[Card], current_trick: list[PlayedCard]) -> GameState:
    current_player = 0
    players = [PlayerState(player_id=current_player, name="cur", own_hand=list(hand))]
    return GameState(
        round_nr=1,
        round_count=10,
        dealer_id=0,
        player_count=1,
        scoreboard=Scoreboard(),
        players=players,
        phase=Phase.PLAY,
        round_state=RoundState(current_trump_suit=None),
        trick_state=TrickState(
            starting_player=0, current_player=current_player, current_trick=current_trick
        ),
    )


class TestComputeDemandedSuit:
    @pytest.mark.parametrize(
        "current_trick, expected",
        [
            # empty trick: no determined card -> no demanded suit.
            (trick(), None),
            # first non-CLANKER card is a SINGULARITY -> free
            (trick(SINGULARITY), None),
            (trick(SINGULARITY, card(Suit.RED, 5)), None),
            # only CLANKER so far -> no demanded suit.
            (trick(CLANKER), None),
            (trick(CLANKER, CLANKER), None),
            # CLANKER in the start gets skipped, then first color counts
            (trick(CLANKER, card(Suit.RED, 5)), Suit.RED),
            (trick(CLANKER, CLANKER, card(Suit.GREEN, 2)), Suit.GREEN),
            # CLANKER, then SINGULARITY -> no suit.
            (trick(CLANKER, SINGULARITY), None),
            (trick(CLANKER, SINGULARITY, card(Suit.RED, 5)), None),
            # normal color leads -> that color is demanded
            (trick(card(Suit.RED, 5)), Suit.RED),
            (trick(card(Suit.RED, 5), card(Suit.BLUE, 3)), Suit.RED),
        ],
    )
    def test_compute_demanded_suit(self, current_trick, expected):
        assert compute_demanded_suit(current_trick) == expected


class TestGetAllowedSuits:
    def test_leading_player_may_play_anything(self):
        allowed = get_allowed_suits(trick(), [card(Suit.RED), card(Suit.BLUE)])
        assert allowed == set(Suit)

    def test_singularity_led_trick_allows_anything(self):
        allowed = get_allowed_suits(trick(SINGULARITY), [card(Suit.RED), card(Suit.BLUE)])
        assert allowed == set(Suit)

    def test_must_follow_demanded_suit_when_held(self):
        # hand has the demanded RED -> only RED (or always CLANKER/SINGULARITY).
        hand = [card(Suit.RED, 4), card(Suit.BLUE, 9)]
        allowed = get_allowed_suits(trick(card(Suit.RED, 2)), hand)
        assert allowed == {Suit.RED, Suit.CLANKER, Suit.SINGULARITY}

    def test_free_choice_when_demanded_suit_not_held(self):
        hand = [card(Suit.BLUE, 9), card(Suit.GREEN, 3)]
        allowed = get_allowed_suits(trick(card(Suit.RED, 2)), hand)
        assert allowed == set(Suit)

    def test_clanker_lead_then_colour_still_demands_colour(self):
        hand = [card(Suit.RED, 4), card(Suit.YELLOW, 9)]
        allowed = get_allowed_suits(trick(CLANKER, card(Suit.RED, 2)), hand)
        assert allowed == {Suit.RED, Suit.CLANKER, Suit.SINGULARITY}


class TestIsLegalCardPlay:
    def test_clanker_and_singularity_always_legal_when_following(self):
        # RED demanded, PLAYER has RED -> CLANKER/SINGULARITY still allowed.
        state = make_state(
            hand=[card(Suit.RED, 4), CLANKER, SINGULARITY],
            current_trick=trick(card(Suit.RED, 2)),
        )
        assert is_legal_card_play(state, CLANKER)
        assert is_legal_card_play(state, SINGULARITY)

    def test_must_follow_demanded_suit(self):
        state = make_state(
            hand=[card(Suit.RED, 4), card(Suit.BLUE, 9)],
            current_trick=trick(card(Suit.RED, 2)),
        )
        assert is_legal_card_play(state, card(Suit.RED, 4))
        assert not is_legal_card_play(state, card(Suit.BLUE, 9))

    def test_any_card_when_demanded_suit_not_held(self):
        state = make_state(
            hand=[card(Suit.BLUE, 9), card(Suit.GREEN, 3)],
            current_trick=trick(card(Suit.RED, 2)),
        )
        assert is_legal_card_play(state, card(Suit.BLUE, 9))
        assert is_legal_card_play(state, card(Suit.GREEN, 3))

    def test_leading_player_may_play_any_card(self):
        state = make_state(
            hand=[card(Suit.RED, 4), card(Suit.BLUE, 9), CLANKER, SINGULARITY],
            current_trick=trick(),
        )
        for c in state.players[0].own_hand:
            assert is_legal_card_play(state, c)
