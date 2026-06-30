from pydantic import BaseModel


class Config(BaseModel):
    player_count: int = 3
    round_count: int = 5

