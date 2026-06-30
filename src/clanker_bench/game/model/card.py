from enum import Enum

import pydantic

class Suit(str, Enum):
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
