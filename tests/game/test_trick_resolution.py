"""Tests for who wins a trick ("Stich").

Rule (German original):
  - Der erste gespielte SINGULARITY sticht immer.
  - Ist kein SINGULARITY gespielt worden, so sticht der hoechste Trumpf ueber die
    anderen Karten.
  - Sind kein SINGULARITY und kein Trumpf gespielt worden, so bekommt derjenige
    Spieler den Stich, der die hoechste Karte der geforderten Farbe gespielt hat.
  - Ein CLANKER macht keinen Stich, es sei denn, in einem Stich werden nur CLANKER
    gespielt. In diesem Fall gewinnt der erste CLANKER den Stich.
"""
from clanker_bench.game import engine
from clanker_bench.game.model.card import Card, Suit
from tests.game.conftest import make_state

CLANKER = Card(suit=Suit.CLANKER)
SINGULARITY = Card(suit=Suit.SINGULARITY)


def card(suit: Suit, rank: int = 1) -> Card:
    return Card(suit=suit, rank=rank)


class TestIsHigherCard:
    def test_singularity_beats_trump(self):
        assert engine._is_higher_card(SINGULARITY, card(Suit.GREEN, 13), Suit.GREEN, Suit.RED)
        assert not engine._is_higher_card(card(Suit.GREEN, 13), SINGULARITY, Suit.GREEN, Suit.RED)

    def test_trump_beats_demanded_and_offsuit(self):
        # Trump GREEN, demanded RED.
        assert engine._is_higher_card(card(Suit.GREEN, 2), card(Suit.RED, 13), Suit.GREEN, Suit.RED)
        assert not engine._is_higher_card(card(Suit.RED, 13), card(Suit.GREEN, 2), Suit.GREEN, Suit.RED)

    def test_higher_trump_beats_lower_trump(self):
        assert engine._is_higher_card(card(Suit.GREEN, 10), card(Suit.GREEN, 5), Suit.GREEN, Suit.RED)
        assert not engine._is_higher_card(card(Suit.GREEN, 5), card(Suit.GREEN, 10), Suit.GREEN, Suit.RED)

    def test_demanded_beats_offsuit(self):
        # No trump; demanded RED beats an unrelated colour regardless of rank.
        assert engine._is_higher_card(card(Suit.RED, 2), card(Suit.BLUE, 13), None, Suit.RED)
        assert not engine._is_higher_card(card(Suit.BLUE, 13), card(Suit.RED, 2), None, Suit.RED)

    def test_higher_rank_wins_within_demanded_suit(self):
        assert engine._is_higher_card(card(Suit.RED, 10), card(Suit.RED, 5), None, Suit.RED)
        assert not engine._is_higher_card(card(Suit.RED, 5), card(Suit.RED, 10), None, Suit.RED)

    def test_clanker_loses_to_everything(self):
        assert not engine._is_higher_card(CLANKER, card(Suit.RED, 1), None, Suit.RED)
        assert engine._is_higher_card(card(Suit.RED, 1), CLANKER, None, Suit.RED)

    def test_equal_tier_does_not_override_first(self):
        # Two SINGULARITY / two CLANKER: the later one must NOT count as higher,
        # so the first-played one stays the winner.
        assert not engine._is_higher_card(SINGULARITY, SINGULARITY, Suit.GREEN, Suit.RED)
        assert not engine._is_higher_card(CLANKER, CLANKER, Suit.GREEN, Suit.RED)


class TestDetermineTrickWinner:
    # `current_trick` nimmt rohe Cards an -> player_id = Reihenfolge (via conftest-Factory).
    def test_first_singularity_always_wins(self):
        state = make_state(current_trick=[card(Suit.RED, 5), SINGULARITY, card(Suit.GREEN, 13)], trump=Suit.GREEN)
        assert engine._determine_trick_winner(state) == 1

    def test_first_of_several_singularities_wins(self):
        state = make_state(current_trick=[card(Suit.RED, 5), SINGULARITY, SINGULARITY], trump=Suit.GREEN)
        assert engine._determine_trick_winner(state) == 1

    def test_highest_trump_wins_without_singularity(self):
        state = make_state(current_trick=[card(Suit.RED, 5), card(Suit.GREEN, 3), card(Suit.RED, 9)], trump=Suit.GREEN)
        assert engine._determine_trick_winner(state) == 1

    def test_highest_demanded_wins_without_trump_or_singularity(self):
        state = make_state(current_trick=[card(Suit.RED, 2), card(Suit.RED, 13), card(Suit.RED, 7)], trump=None)
        assert engine._determine_trick_winner(state) == 1

    def test_offsuit_card_never_wins(self):
        # No trump; demanded is RED, an off-suit GREEN must not win even with high rank.
        state = make_state(current_trick=[card(Suit.RED, 5), card(Suit.GREEN, 13), card(Suit.RED, 9)], trump=None)
        assert engine._determine_trick_winner(state) == 2

    def test_clanker_does_not_win_against_colour(self):
        state = make_state(current_trick=[CLANKER, card(Suit.RED, 5), card(Suit.RED, 9)], trump=None)
        assert engine._determine_trick_winner(state) == 2

    def test_only_clankers_first_clanker_wins(self):
        state = make_state(current_trick=[CLANKER, CLANKER, CLANKER], trump=Suit.GREEN)
        assert engine._determine_trick_winner(state) == 0

    def test_clanker_lead_then_singularity_wins(self):
        # CLANKER leads (no influence), SINGULARITY is first real card -> it wins.
        state = make_state(current_trick=[CLANKER, SINGULARITY, card(Suit.GREEN, 13)], trump=Suit.GREEN)
        assert engine._determine_trick_winner(state) == 1
