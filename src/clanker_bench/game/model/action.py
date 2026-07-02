from typing import Annotated, Literal

import pydantic

from clanker_bench.game.model.card import Card, Suit

class PredictTricksAction(pydantic.BaseModel):
    type: Literal["predict_tricks"] = "predict_tricks"
    trick_count: int = pydantic.Field(ge=0)


class PlayCardAction(pydantic.BaseModel):
    type: Literal["play_card"] = "play_card"
    card: Card

class SelectTrumpAction(pydantic.BaseModel):
    type: Literal["select_trump"] = "select_trump"
    suit: Suit


GameAction = Annotated[
    PredictTricksAction | PlayCardAction | SelectTrumpAction,
    pydantic.Field(discriminator="type"),
]