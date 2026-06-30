from hypothesis import given

from clanker_bench.game import engine
from clanker_bench.game.model.card import Card, Suit
from clanker_bench.game.model.gamestate import GameState, RoundState, TrickState
from clanker_bench.game.model.scoreboard import Scoreboard
import hypothesis.strategies as st

class TestRemoveCardFromHand:
    def test_remove_card_from_hand(self):
        # Arrange
        card: Card = Card(suit=Suit.BLUE, rank=10)
        expected_hand = [Card(suit=Suit.BLUE, rank=1), Card(suit=Suit.CLANKER), Card(suit=Suit.SINGULARITY)]
        hand: list[Card] = [*expected_hand, card]

        # Act
        new_hand = engine._remove_card_from_hand(card, hand)

        # Assert
        assert len(new_hand) == (len(hand) - 1)
        assert new_hand == expected_hand
        assert len(new_hand) == len(expected_hand)
        assert (card not in new_hand)

    def test_removes_card_just_once(self):
        # Arrange
        card: Card = Card(suit=Suit.CLANKER)
        hand = [card, Card(suit=Suit.BLUE, rank=1), Card(suit=Suit.CLANKER), Card(suit=Suit.SINGULARITY)]

        # Act
        new_hand = engine._remove_card_from_hand(card, hand)

        # Assert
        assert len(new_hand) == (len(hand) - 1)
        assert (card in new_hand)
        assert(new_hand.count(card) == 1)

    def test_removes_card_twice(self):
        # Arrange
        card: Card = Card(suit=Suit.CLANKER)
        hand = [card, Card(suit=Suit.BLUE, rank=1), Card(suit=Suit.CLANKER), Card(suit=Suit.SINGULARITY)]

        # Act
        new_hand = engine._remove_card_from_hand(card, hand)
        new_hand = engine._remove_card_from_hand(card, new_hand)

        assert len(new_hand) == (len(hand) - 2)
        assert (card not in new_hand)

    def test_remove_nonexistent_card(self):
        # Arrange
        card: Card = Card(suit=Suit.CLANKER)
        hand = [Card(suit=Suit.SINGULARITY), Card(suit=Suit.SINGULARITY)]

        # Act
        new_hand = engine._remove_card_from_hand(card, hand)
        assert len(new_hand) == (len(hand))
        assert (card not in new_hand)


def generate_test_state(player_count: int, starting_player: int, current_player: int) -> GameState:
    gamestate: GameState = GameState(
        player_count=player_count,
        current_player=current_player,
        round_nr=10,
        scoreboard=Scoreboard(),
        players=[],
        round_state=RoundState(
            current_trump_suit=Suit.BLUE,
            awaiting_trump_select=False,
        ),
        trick_state=TrickState(starting_player=starting_player),
    )
    return gamestate


class TestTrickComplete:
     # def _trick_complete (state: GameState) -> bool:
     #    next_player = (state.current_player + 1) % state.player_count
     #    return next_player == state.starting_player

    def test_is_trick_should_complete(self):
        state = generate_test_state(player_count=2, starting_player=1, current_player=0)
        trick_complete = engine._is_trick_complete(state)

        assert trick_complete

    def test_is_trick_should_not_complete(self):
        state = generate_test_state(player_count=2, starting_player=1, current_player=1)
        trick_complete = engine._is_trick_complete(state)

        assert not trick_complete

    def test_is_trick_should_complete_modulo(self):
        state = generate_test_state(player_count=2, starting_player=0, current_player=1)
        trick_complete = engine._is_trick_complete(state)

        assert trick_complete

    @given(
            data=st.integers(min_value=2, max_value=6).flatmap(
                lambda player_count: st.tuples(
                    st.just(player_count),
                    st.integers(min_value=0, max_value=player_count - 1),
                    st.integers(min_value=0, max_value=player_count - 1),
                )
            )
     )
    def test_trick_found_always_once_per_rotation(self, data):
        player_count, starting_player, current_player = data
        state = generate_test_state(player_count, starting_player, current_player)
        trick_found_count = 0
        for player in range(player_count):
            state.current_player = (starting_player + player) % player_count
            trick_complete = engine._is_trick_complete(state)
            if trick_complete:
               trick_found_count =+ 1

        assert trick_found_count == 1

    @given(
            data=st.integers(min_value=2, max_value=6).flatmap(
                lambda player_count: st.tuples(
                    st.just(player_count),
                    st.integers(min_value=0, max_value=player_count - 1),
                )
            )
     )
    def test_trick_found_at_starting_player_minus_one(self, data):
        player_count, starting_player = data
        current_player = (starting_player - 1) % player_count
        state = generate_test_state(player_count, starting_player, current_player)

        assert engine._is_trick_complete(state)

class TestNextPlayer:

    @given( current_player=st.integers(
        min_value=0, max_value=6),
        player_count=st.integers(min_value=2, max_value=6)
    )
    def test_next_player(self, current_player, player_count):
        state = generate_test_state(player_count, 0, current_player)
        next_state = engine._next_player(state)
        next_player = (current_player + 1) % player_count
        assert next_player == next_state.current_player

    def test_next_player_fixed(self):
        state = generate_test_state(player_count=2, starting_player=0, current_player=1)
        next_state = engine._next_player(state)
        assert next_state.current_player == 0