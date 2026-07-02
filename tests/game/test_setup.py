"""Tests for game setup (new_game).

Rules:
  - In der ersten Runde bekommt jeder Spieler eine Spielkarte.
  - Die oberste verbleibende Karte bestimmt die Trumpffarbe (CLANKER/SINGULARITY
    -> kein fester Trumpf; SINGULARITY -> Geber waehlt).
  - Trumpf ist nie eine CLANKER- oder SINGULARITY-"Farbe".
"""
import random

import pytest

from clanker_bench.game import setup
from clanker_bench.game.deck import determine_trump, init_deck, shuffle_deck
from clanker_bench.game.model.card import Suit
from clanker_bench.game.model.config import Config
from clanker_bench.game.model.gamestate import Phase
from clanker_bench.game.setup import new_game

SEEDS = [0, 1, 2, 7, 42, 123, 999]


@pytest.mark.parametrize("player_count", [3, 4, 5, 6])
def test_creates_one_state_per_player(player_count):
    state = new_game(Config(player_count=player_count), seed=0)
    assert len(state.players) == player_count
    assert state.player_count == player_count


@pytest.mark.parametrize("player_count", [3, 4, 5, 6])
def test_round_one_deals_single_card_each(player_count):
    state = new_game(Config(player_count=player_count), seed=0)
    assert all(len(p.own_hand) == 1 for p in state.players)


@pytest.mark.parametrize("seed", SEEDS)
def test_trump_matches_revealed_top_card(seed):
    # Replicate the deal deterministically to know the revealed top card.
    deck = shuffle_deck(init_deck(), setup._round_rng(seed, round_nr=0))
    expected_trump, expected_awaiting = determine_trump([deck[3]])

    state = new_game(Config(player_count=3), seed=seed)
    assert state.round_state.current_trump_suit == expected_trump
    assert state.phase == Phase.SELECT_TRUMP if expected_awaiting else state.phase != Phase.SELECT_TRUMP


@pytest.mark.parametrize("seed", SEEDS)
def test_trump_is_never_a_special_suit(seed):
    state = new_game(Config(player_count=3), seed=seed)
    assert state.round_state.current_trump_suit in {None, *(Suit.RED, Suit.BLUE, Suit.GREEN, Suit.YELLOW)}


@pytest.mark.parametrize("seed", SEEDS)
def test_awaiting_trump_implies_no_trump_yet(seed):
    state = new_game(Config(player_count=3), seed=seed)
    if state.phase == Phase.SELECT_TRUMP:
        assert state.round_state.current_trump_suit is None

def test_player_names_are_unique():
    # Every player has unique name
    state = new_game(Config(player_count=4), seed=0)
    names = [p.name for p in state.players]
    assert len(set(names)) == len(names)
