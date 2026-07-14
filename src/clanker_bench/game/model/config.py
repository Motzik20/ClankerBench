from pydantic import BaseModel


class Config(BaseModel):
    player_count: int = 3

