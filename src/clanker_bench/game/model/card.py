from enum import StrEnum

import pydantic


class Suit(StrEnum):
    BLUE = "Blue"
    GREEN = "Green"
    RED = "Red"
    YELLOW = "Yellow"
    CLANKER = "Clanker"
    SINGULARITY = "Singularity"


class Card(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)

    rank: int = 0
    suit: Suit
