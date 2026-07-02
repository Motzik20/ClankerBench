import pytest

from clanker_bench.game.model.card import Card, Suit
from clanker_bench.game.model.gamestate import (
    GameState,
    Phase,
    PlayedCard,
    RoundState,
    TrickState,
)
from clanker_bench.game.model.player_state import PlayerState
from clanker_bench.game.model.scoreboard import Scoreboard


def card(suit: Suit, rank: int = 1) -> Card:
    return Card(suit=suit, rank=rank)


def played_card(player_id: int, card: Card) -> PlayedCard:
    return PlayedCard(player_id=player_id, card=card)


def _to_played_cards(current_trick) -> list[PlayedCard]:
    """Accept either PlayedCard or raw Card (then player_id = order)."""
    result: list[PlayedCard] = []
    for i, entry in enumerate(current_trick):
        if isinstance(entry, PlayedCard):
            result.append(entry)
        else:
            result.append(PlayedCard(player_id=i, card=entry))
    return result


def make_state(
    *,
    phase: Phase = Phase.PLAY,
    player_count: int = 3,
    hands: list[list[Card]] | None = None,
    starting_player: int = 0,
    current_player: int | None = None,
    current_trick=(),
    trump: Suit | None = None,
    predicted: list[int] | None = None,
    actual: list[int] | None = None,
    trick_nr: int = 0,
    round_nr: int = 5,
    round_count: int = 20,
    dealer_id: int | None = None,
    played_cards=(),
    scoreboard: Scoreboard | None = None,
    seed: int = 0,
) -> GameState:
    if current_player is None:
        current_player = starting_player
    if dealer_id is None:
        dealer_id = (starting_player - 1) % player_count
    if hands is None:
        hands = [[] for _ in range(player_count)]
    if predicted is None:
        predicted = [-1] * player_count
    if actual is None:
        actual = [0] * player_count
    if scoreboard is None:
        scoreboard = Scoreboard()
    players = [
        PlayerState(player_id=i, name=f"P{i}", own_hand=list(hands[i]))
        for i in range(player_count)
    ]
    return GameState(
        seed=seed,
        phase=phase,
        round_count=round_count,
        round_nr=round_nr,
        player_count=player_count,
        scoreboard=scoreboard,
        players=players,
        round_state=RoundState(
            trick_nr=trick_nr,
            dealer_id=dealer_id,
            current_trump_suit=trump,
            predicted_player_tricks=list(predicted),
            actual_player_tricks=list(actual),
            played_cards=_to_played_cards(played_cards),
        ),
        trick_state=TrickState(
            starting_player=starting_player,
            current_player=current_player,
            current_trick=_to_played_cards(current_trick),
        ),
    )