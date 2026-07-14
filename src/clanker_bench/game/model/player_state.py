import pydantic

from clanker_bench.game.model.card import Card


class PlayerState(pydantic.BaseModel):
    player_id: int
    name: str
    own_hand: list[Card]
