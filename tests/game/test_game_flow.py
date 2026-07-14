"""Tests for overall game flow / round progression.

Rules:
  - In Runde r bekommt jeder Spieler r Karten (Runde 1 -> 1 Karte, usw.).
  - 60 Karten geteilt durch die Spielerzahl ergibt die Rundenzahl
    (3 -> 20, 4 -> 15, 5 -> 12, 6 -> 10 Runden).
  - In der letzten Runde werden alle Karten ausgeteilt; es gibt keinen Trumpf.

"""

import pytest

from clanker_bench.game.deck import deal_cards, init_deck
from clanker_bench.game.model.config import Config
from clanker_bench.game.setup import new_game

DECK_SIZE = 60
ROUNDS_BY_PLAYER_COUNT = {3: 20, 4: 15, 5: 12, 6: 10}


class TestRoundStructure:
    @pytest.mark.parametrize(
        "player_count, expected_rounds", ROUNDS_BY_PLAYER_COUNT.items(),
    )
    def test_round_count_is_deck_divided_by_players(
        self, player_count, expected_rounds,
    ):
        assert (
            new_game(Config(player_count=player_count), 0).round_count
            == expected_rounds
        )

    @pytest.mark.parametrize("player_count, rounds", ROUNDS_BY_PLAYER_COUNT.items())
    def test_last_round_deals_out_the_whole_deck(self, player_count, rounds):
        assert player_count * rounds == DECK_SIZE

    @pytest.mark.parametrize("round_nr", [1, 2, 3, 5, 10])
    def test_round_deals_round_number_of_cards(self, round_nr):
        deck = init_deck()
        dealt, _ = deal_cards(round_nr, deck)
        assert len(dealt) == round_nr


@pytest.mark.skip(reason="Orchestrierung noch nicht implementiert - Spec fuer TDD")
class TestRoundOrchestration:
    def test_prediction_starts_left_of_dealer(self):
        # Der Spieler links vom Geber gibt die erste Prognose ab und spielt zuerst aus.
        raise NotImplementedError

    def test_dealer_rotates_each_round(self):
        # Vor jeder Runde wechselt der Geber.
        raise NotImplementedError

    def test_last_round_has_no_trump(self):
        # In der letzten Runde bleibt keine Karte uebrig -> keine Trumpffarbe.
        raise NotImplementedError

    def test_sitting_out_player_gets_average_of_others(self):
        # Setzt ein Spieler aus, bekommt er den Durchschnitt des Ertrags der anderen.
        raise NotImplementedError
