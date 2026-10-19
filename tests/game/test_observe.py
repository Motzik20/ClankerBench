"""Tests fuer `observe()`: Ein Spieler sieht seine eigene Hand und alles
Oeffentliche, aber nie die Karten der anderen Spieler.

Jeder Test spielt ganze Zufallsspiele durch, damit alle Phasen abgedeckt sind.
"""

import random
from collections.abc import Iterator

import pytest

from clanker_bench.game.engine import get_action_space, observe, step
from clanker_bench.game.model.config import Config
from clanker_bench.game.model.gamestate import GameState, Phase
from clanker_bench.game.setup import new_game

GAMES = [(player_count, seed) for player_count in (3, 4, 6) for seed in (0, 1)]


def _random_game_states(player_count: int, seed: int) -> Iterator[GameState]:
    rng = random.Random(seed)
    state = new_game(Config(player_count=player_count), seed=seed)
    while state.phase != Phase.FINISHED:
        yield state
        state = step(state, rng.choice(get_action_space(state)))


def _shuffle_other_hands(
    state: GameState, player_id: int, rng: random.Random
) -> GameState:
    """Verteilt die Karten der anderen Spieler neu, Handgroessen bleiben gleich."""
    others = [p for p in state.players if p.player_id != player_id]
    pool = [card for p in others for card in p.own_hand]
    rng.shuffle(pool)
    new_players = []
    for p in state.players:
        if p.player_id == player_id:
            new_players.append(p)
            continue
        hand, pool = pool[: len(p.own_hand)], pool[len(p.own_hand) :]
        new_players.append(p.model_copy(update={"own_hand": hand}))
    return state.model_copy(update={"players": new_players})


@pytest.mark.parametrize(("player_count", "seed"), GAMES)
def test_own_hand_is_the_observers_hand(player_count, seed):
    for state in _random_game_states(player_count, seed):
        for player in state.players:
            obs = observe(state, player.player_id)
            assert obs.own_hand == player.own_hand


@pytest.mark.parametrize(("player_count", "seed"), GAMES)
def test_observation_does_not_depend_on_other_hands(player_count, seed):
    # Haengt die Observation von fremden Karten ab, aendert sie sich beim Mischen.
    rng = random.Random(seed)
    for state in _random_game_states(player_count, seed):
        for player_id in range(state.player_count):
            shuffled = _shuffle_other_hands(state, player_id, rng)
            assert observe(shuffled, player_id) == observe(state, player_id)


@pytest.mark.parametrize(("player_count", "seed"), GAMES)
def test_public_fields_match_state(player_count, seed):
    for state in _random_game_states(player_count, seed):
        for player_id in range(state.player_count):
            obs = observe(state, player_id)
            assert obs.player_id == player_id
            assert obs.dealer_id == state.round_state.dealer_id
            assert obs.current_trump_suit == state.round_state.current_trump_suit
            assert obs.trick_state == state.trick_state
            assert obs.played_cards == state.round_state.played_cards
            assert (
                obs.predicted_player_tricks == state.round_state.predicted_player_tricks
            )
            assert obs.actual_player_tricks == state.round_state.actual_player_tricks


def test_changing_observation_does_not_change_state():
    state = new_game(Config(player_count=3), seed=0)
    before = state.model_dump()
    obs = observe(state, 0)
    obs.own_hand.clear()
    obs.predicted_player_tricks.append(99)
    obs.trick_state.current_trick.clear()
    assert state.model_dump() == before
