"""Tests for round scoring ("Bewertung und Buchfuehrung").

Standard scoring rule:
  - Prognose richtig: 20 Punkte fuer die richtige Prognose + 10 Punkte pro Stich.
  - Prognose falsch: pro Stich Abweichung 10 Punkte Abzug.

Documented examples:
  - 3 angesagt, 3 bekommen  -> 20 + 3*10        = 50
  - 4 angesagt, 2 bekommen  -> (2 - 4) * 10      = -20
  - 0 angesagt, 0 bekommen  -> 20                = 20
"""
import pytest

from clanker_bench.game import engine
from clanker_bench.game.model.gamestate import GameState, RoundState, TrickState, Phase
from clanker_bench.game.model.scoreboard import Scoreboard


def make_state(predicted: list[int], actual: list[int]) -> GameState:
    return GameState(
        round_nr=1,
        round_count=10,
        dealer_id=0,
        player_count=len(predicted),
        scoreboard=Scoreboard(),
        players=[],
        phase=Phase.PLAY,
        round_state=RoundState(
            current_trump_suit=None,
            predicted_player_tricks=list(predicted),
            actual_player_tricks=list(actual),
        ),
        trick_state=TrickState(starting_player=0, current_player=0),
    )


class TestRoundScore:
    @pytest.mark.parametrize(
        "predicted, actual, expected",
        [
            ([3], [3], [50]),                 # right Prediction: 20 + 30
            ([4], [2], [-20]),                # 2 below : -10 * 2
            ([0], [0], [20]),                 # 0 predicted, 0 gotten
            ([2], [5], [-30]),                # 3 to much: -10 * 3
            ([1], [0], [-10]),                # 1 below
            ([5], [5], [70]),                 # right Prediction 20 + 50
            ([3, 4, 0], [3, 2, 0], [50, -20, 20]),  # multiple players combined
        ],
    )
    def test_round_score(self, predicted, actual, expected):
        result = engine._calculate_round_score(make_state(predicted, actual))
        assert result is not None, "_calculate_round_score muss ein Ergebnis liefern"
        assert result.round_score == expected
