"""Tests for deck construction and dealing.

Rules:
  - 60 Karten: 4 Farben mit Rang 1..13, plus je 4 CLANKER und 4 SINGULARITY.
  - Die oberste Karte bestimmt die Trumpffarbe; ist sie ein CLANKER -> kein Trumpf;
    ist sie ein SINGULARITY -> der Geber waehlt (awaiting_trump_select).
"""

import random

import pytest

from clanker_bench.game.deck import deal_cards, determine_trump, init_deck, shuffle_deck
from clanker_bench.game.model.card import Card, Suit

COLOURS = [Suit.RED, Suit.BLUE, Suit.GREEN, Suit.YELLOW]


class TestInitDeck:
    def test_total_card_count(self):
        assert len(init_deck()) == 60

    @pytest.mark.parametrize("colour", COLOURS)
    def test_thirteen_ranks_per_colour(self, colour):
        deck = init_deck()
        ranks = sorted(c.rank for c in deck if c.suit == colour)
        assert ranks == list(range(1, 14))

    @pytest.mark.parametrize("special", [Suit.CLANKER, Suit.SINGULARITY])
    def test_four_of_each_special(self, special):
        deck = init_deck()
        assert sum(1 for c in deck if c.suit == special) == 4


class TestDetermineTrump:
    @pytest.mark.parametrize("colour", COLOURS)
    def test_colour_card_sets_trump(self, colour):
        assert determine_trump([Card(suit=colour, rank=7)]) == (colour, False)

    def test_clanker_means_no_trump(self):
        assert determine_trump([Card(suit=Suit.CLANKER)]) == (None, False)

    def test_singularity_means_dealer_selects(self):
        assert determine_trump([Card(suit=Suit.SINGULARITY)]) == (None, True)


class TestDealCards:
    def test_deals_requested_count(self):
        deck = init_deck()
        dealt, remaining = deal_cards(5, deck)
        assert len(dealt) == 5
        assert len(remaining) == 55

    def test_dealt_plus_remaining_is_whole_deck(self):
        deck = init_deck()
        dealt, remaining = deal_cards(7, deck)
        assert dealt + remaining == deck


class TestShuffleDeck:
    def test_shuffle_preserves_multiset(self):
        deck = init_deck()
        shuffled = shuffle_deck(deck, random.Random(123))
        assert sorted(shuffled, key=lambda c: (c.suit.value, c.rank)) == sorted(
            deck, key=lambda c: (c.suit.value, c.rank),
        )

    def test_shuffle_is_deterministic_for_seed(self):
        deck = init_deck()
        assert shuffle_deck(deck, random.Random(1)) == shuffle_deck(
            deck, random.Random(1),
        )
