import pydantic

from clanker_bench.game.model.card import Suit, Card
from clanker_bench.game.model.player_state import PlayerState
from clanker_bench.game.model.scoreboard import Scoreboard


class PlayedCard(pydantic.BaseModel):
     player_id: int
     card: Card

class TrickState(pydantic.BaseModel):
     starting_player: int
     current_trick: list[PlayedCard] = pydantic.Field(default_factory=list)

class RoundState(pydantic.BaseModel):
     trick_nr: int = pydantic.Field(0)
     current_trump_suit: Suit | None
     awaiting_trump_select: bool
     predicted_player_tricks: list[int] = pydantic.Field(default_factory=list)
     actual_player_tricks: list[int] = pydantic.Field(default_factory=list)

class Observation(pydantic.BaseModel):
     own_hand: list[Card] = pydantic.Field(default_factory=list)
     current_trump_suit: Suit | None
     current_trick: list[PlayedCard] = pydantic.Field(default_factory=list)
     played_cards: list[PlayedCard] = pydantic.Field(default_factory=list)
     predicted_player_tricks: list[int | None] = pydantic.Field(default_factory=list)
     actual_player_tricks: list[int] = pydantic.Field(default_factory=list)

class GameState(pydantic.BaseModel):
     round_nr: int
     player_count: int
     current_player: int
     scoreboard: Scoreboard
     players: list[PlayerState]
     round_state: RoundState
     trick_state: TrickState
     played_cards: list[PlayedCard] = pydantic.Field(default_factory=list)

