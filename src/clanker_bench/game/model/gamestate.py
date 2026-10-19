from enum import StrEnum

import pydantic

from clanker_bench.game.model.card import Card, Suit
from clanker_bench.game.model.player_state import PlayerState
from clanker_bench.game.model.scoreboard import Scoreboard


class PlayedCard(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(use_attribute_docstrings=True)

    player_id: int
    """Absolute id of the player who played the card."""
    card: Card
    """The card that was played."""


class TrickState(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(use_attribute_docstrings=True)

    starting_player: int
    """PREDICT: the player who bids first (left of the dealer). PLAY: the player who leads the current trick (winner of the previous one)."""
    current_player: int
    """The player whose turn it is in PREDICT and PLAY. Not used in SELECT_TRUMP, where the dealer acts."""
    current_trick: list[PlayedCard] = pydantic.Field(default_factory=list)
    """Cards of the trick in progress, in play order. Moved into RoundState.played_cards and emptied once the trick is complete."""


class RoundState(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(use_attribute_docstrings=True)

    trick_nr: int = pydantic.Field(default=0)
    """Zero-based number of the trick in progress. Goes past round_nr once the last trick of the round is finished."""
    dealer_id: int
    """The dealer of this round. Chooses trump if a Singularity is revealed and bids last, with the restriction on the final bid."""
    current_trump_suit: Suit | None
    """Trump suit of this round. None if there is no trump (Clanker revealed or no card left) or the dealer has not chosen yet."""
    predicted_player_tricks: list[int] = pydantic.Field(default_factory=list)
    """Bid per player, indexed by player id. -1 means not bid yet."""
    actual_player_tricks: list[int] = pydantic.Field(default_factory=list)
    """Tricks won so far this round, indexed by player id."""
    played_cards: list[PlayedCard] = pydantic.Field(default_factory=list)
    """Cards of all finished tricks this round, in play order. Does not include current_trick. Starts empty each round."""


class Observation(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(use_attribute_docstrings=True)

    own_hand: list[Card] = pydantic.Field(default_factory=list)
    """Cards in the observing player's hand. Never other players' hands."""
    current_trump_suit: Suit | None
    """See RoundState.current_trump_suit."""
    trick_state: TrickState
    """See TrickState"""
    played_cards: list[PlayedCard] = pydantic.Field(default_factory=list)
    """See RoundState.played_cards."""
    predicted_player_tricks: list[int] = pydantic.Field(default_factory=list)
    """Bid per player, indexed by player id. -1 means not bid yet."""
    actual_player_tricks: list[int] = pydantic.Field(default_factory=list)
    """See RoundState.actual_player_tricks."""
    player_id: int
    """The player whose State is observed."""
    dealer_id: int
    """See RoundState.dealer_id."""


class Phase(StrEnum):
    SELECT_TRUMP = "select_trump"
    PREDICT = "predict"
    PLAY = "play"
    FINISHED = "finished"


class GameState(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(use_attribute_docstrings=True)

    seed: int = pydantic.Field(default=0)
    """Game seed. Each round's deal is derived from seed and round_nr."""
    phase: Phase
    """Which kind of action is expected next."""
    round_count: int
    """Total number of rounds in the game."""
    round_nr: int
    """Zero-based round number. Each player holds round_nr + 1 cards at the start."""
    player_count: int
    """Number of players (3 to 6)."""
    scoreboard: Scoreboard
    """Scores of all finished rounds."""
    players: list[PlayerState]
    """Per-player state including hidden hands, indexed by player id."""
    round_state: RoundState
    """State that lasts one round."""
    trick_state: TrickState
    """State that lasts one trick."""
