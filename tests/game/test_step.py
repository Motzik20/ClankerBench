"""End-to-end tests for the three `step()` branches:
SELECT_TRUMP, PREDICT und PLAY — inkl. Phasenuebergaenge.

GameStates kommen aus dem zentralen `make_state`-Fixture (siehe conftest.py).
"""
import pytest

from clanker_bench.game.engine import step
from clanker_bench.game.model.action import (
    PlayCardAction,
    PredictTricksAction,
    SelectTrumpAction,
)
from clanker_bench.game.model.card import Card, Suit
from clanker_bench.game.model.exception import IllegalActionException
from clanker_bench.game.model.gamestate import Phase, PlayedCard
from tests.game.conftest import make_state


def card(suit: Suit, rank: int = 1) -> Card:
    return Card(suit=suit, rank=rank)


def pc(player_id: int, c: Card) -> PlayedCard:
    return PlayedCard(player_id=player_id, card=c)


class TestSelectTrumpBranch:
    def test_sets_trump_and_moves_to_predict(self):
        state = make_state(phase=Phase.SELECT_TRUMP, trump=None)
        new = step(state, SelectTrumpAction(suit=Suit.RED))
        assert new.round_state.current_trump_suit == Suit.RED
        assert new.phase == Phase.PREDICT

    def test_rejected_outside_select_phase(self):
        state = make_state(phase=Phase.PREDICT)
        with pytest.raises(IllegalActionException):
            step(state, SelectTrumpAction(suit=Suit.RED))

    @pytest.mark.parametrize("bad", [Suit.CLANKER, Suit.SINGULARITY])
    def test_rejects_non_colour(self, bad):
        state = make_state(phase=Phase.SELECT_TRUMP)
        with pytest.raises(IllegalActionException):
            step(state, SelectTrumpAction(suit=bad))


class TestPredictBranch:
    # 3 Spieler, Dealer=0 => Ausspieler/Erst-Schaetzer=1, Reihenfolge 1, 2, 0.
    # round_nr=2 => 3 Stiche, gueltige Prognosen 0..3.
    @staticmethod
    def _state(make_state, **kw):
        return make_state(
            phase=Phase.PREDICT, player_count=3, starting_player=1,
            dealer_id=0, round_nr=2, **kw
        )

    def test_records_prediction_and_advances(self):
        new = step(self._state(make_state), PredictTricksAction(trick_count=2))
        assert new.round_state.predicted_player_tricks[1] == 2
        assert new.trick_state.current_player == 2
        assert new.phase == Phase.PREDICT

    def test_intermediate_prediction_stays_in_predict(self):
        # Nach der ersten von drei Prognosen darf noch nicht gespielt werden.
        new = step(self._state(make_state), PredictTricksAction(trick_count=1))
        assert new.phase == Phase.PREDICT

    def test_all_predictions_then_switch_to_play(self):
        state = self._state(make_state)                            # p1 am Zug
        state = step(state, PredictTricksAction(trick_count=1))     # p1
        state = step(state, PredictTricksAction(trick_count=1))     # p2
        state = step(state, PredictTricksAction(trick_count=0))     # p0 (Dealer, 1 verboten)
        assert state.round_state.predicted_player_tricks == [0, 1, 1]
        assert state.phase == Phase.PLAY
        assert state.trick_state.current_player == 1               # zurueck beim Ausspieler

    def test_rejected_outside_predict_phase(self):
        state = make_state(phase=Phase.PLAY)
        with pytest.raises(IllegalActionException):
            step(state, PredictTricksAction(trick_count=0))

    def test_dealer_cannot_make_total_equal_trick_count(self):
        # p1=1, p2=1 schon angesagt; Dealer p0 darf nicht 1 waehlen (Summe 3 = Stichzahl).
        state = self._state(make_state, predicted=[-1, 1, 1], current_player=0)
        with pytest.raises(IllegalActionException):
            step(state, PredictTricksAction(trick_count=1))


class TestPlayCardBranch:
    # 3 Spieler, Ausspieler=0, kein Trumpf. RED gefordert; hoechste RED gewinnt.
    @staticmethod
    def _state(make_state, hands, **kw):
        return make_state(
            phase=Phase.PLAY, player_count=3, starting_player=0,
            dealer_id=2, trump=None, hands=hands, **kw
        )

    def test_playing_a_card_advances_to_next_player(self):
        hands = [[card(Suit.RED, 5)], [card(Suit.RED, 9)], [card(Suit.RED, 2)]]
        new = step(self._state(make_state, hands), PlayCardAction(card=card(Suit.RED, 5)))
        assert len(new.trick_state.current_trick) == 1
        assert card(Suit.RED, 5) not in new.players[0].own_hand
        assert new.trick_state.current_player == 1
        assert new.phase == Phase.PLAY

    def test_completing_trick_tallies_the_winner(self):
        hands = [[card(Suit.RED, 5)], [card(Suit.RED, 9)], [card(Suit.RED, 2)]]
        state = self._state(make_state, hands)
        state = step(state, PlayCardAction(card=card(Suit.RED, 5)))   # p0
        state = step(state, PlayCardAction(card=card(Suit.RED, 9)))   # p1
        state = step(state, PlayCardAction(card=card(Suit.RED, 2)))   # p2 -> Stich voll
        assert state.round_state.actual_player_tricks[1] == 1        # RED9 gewinnt
        assert state.round_state.trick_nr == 1
        assert state.trick_state.current_trick == []
        assert state.trick_state.starting_player == 1                # Gewinner fuehrt neu
        assert len(state.round_state.played_cards) == 3
        assert state.phase == Phase.PLAY

    def test_last_trick_finishes_round_and_deals_next(self):
        # round_nr=0 => genau 1 Stich; danach Rundenwechsel (round_count=2).
        hands = [[card(Suit.RED, 5)], [card(Suit.RED, 9)], [card(Suit.RED, 2)]]
        state = self._state(make_state, hands, round_nr=0, round_count=2, predicted=[0, 1, 0])
        state = step(state, PlayCardAction(card=card(Suit.RED, 5)))
        state = step(state, PlayCardAction(card=card(Suit.RED, 9)))
        state = step(state, PlayCardAction(card=card(Suit.RED, 2)))   # Runde fertig
        assert len(state.scoreboard.rounds) == 1
        assert state.round_nr == 1
        assert state.phase in (Phase.SELECT_TRUMP, Phase.PREDICT)

    def test_rejected_outside_play_phase(self):
        state = make_state(phase=Phase.PREDICT, hands=[[card(Suit.RED, 5)], [], []])
        with pytest.raises(IllegalActionException):
            step(state, PlayCardAction(card=card(Suit.RED, 5)))

    def test_must_follow_demanded_suit(self):
        # RED gefordert (p0 hat RED5 gelegt), p1 hat RED -> darf nicht BLUE spielen.
        hands = [[], [card(Suit.RED, 9), card(Suit.BLUE, 3)], []]
        state = self._state(make_state, hands, current_player=1, current_trick=(pc(0, card(Suit.RED, 5)),))
        with pytest.raises(IllegalActionException):
            step(state, PlayCardAction(card=card(Suit.BLUE, 3)))
