import pytest

from clanker_bench.game.model.gamestate import GameState, Phase, RoundState, TrickState
from clanker_bench.game.model.player_state import PlayerState
from clanker_bench.game.model.scoreboard import Scoreboard
from clanker_bench.game.rules.predict_trick_rules import legal_trick_predictions


def make_state(predicts: list[int], player_count, dealer_id, round_nr) -> GameState:
    current_player = 0
    return GameState(
        round_nr=round_nr,
        round_count=round_nr,
        player_count=player_count,
        scoreboard=Scoreboard(),
        phase=Phase.PLAY,
        players=[PlayerState(player_id=0, name="test", own_hand=[])],
        round_state=RoundState(
            current_trump_suit=None,
            dealer_id=dealer_id,
            predicted_player_tricks=predicts,
        ),
        trick_state=TrickState(starting_player=0, current_player=current_player),
    )


class TestLegalTrickPredicts:
    @pytest.mark.parametrize(
        "predicted_tricks, expected, dealer_id, player_id, round_nr",
        [
            ([1, -1, 2, 2], [0, 2, 3, 4, 5, 6], 1, 1, 5),
            ([-1, -1, 2, 2], [0, 1, 2, 3], 1, 0, 2),
            ([1, -1, 2, 2], [0, 1, 2, 3], 1, 1, 2),
            ([1, -1, 1, 1], [1, 2, 3], 1, 1, 2),
        ],
    )
    def test_legal_trick_predicts(
        self, predicted_tricks, expected, player_id, dealer_id, round_nr,
    ):
        assert (
            legal_trick_predictions(round_nr, predicted_tricks, dealer_id, player_id)
            == expected
        )
