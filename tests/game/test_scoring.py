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
from tests.game.conftest import make_state


class TestRoundScore:
    @pytest.mark.parametrize(
        "predicted, actual, expected",
        [
            ([3], [3], [50]),  # right Prediction: 20 + 30
            ([4], [2], [-20]),  # 2 below : -10 * 2
            ([0], [0], [20]),  # 0 predicted, 0 gotten
            ([2], [5], [-30]),  # 3 to much: -10 * 3
            ([1], [0], [-10]),  # 1 below
            ([5], [5], [70]),  # right Prediction 20 + 50
            ([3, 4, 0], [3, 2, 0], [50, -20, 20]),  # multiple players combined
        ],
    )
    def test_round_score(self, predicted, actual, expected):
        state = make_state(
            predicted=predicted, actual=actual, player_count=len(predicted),
        )
        result = engine._calculate_round_score(state)
        assert result is not None, "_calculate_round_score muss ein Ergebnis liefern"
        assert result.round_score == expected
