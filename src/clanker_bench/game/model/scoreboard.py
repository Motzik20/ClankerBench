import pydantic


class RoundScore(pydantic.BaseModel):
    predicted_trick_count: list[int]
    actual_trick_count: list[int]
    round_score: list[int]

    @pydantic.model_validator(mode="after")
    def validate_lengths(self):
        same: bool = (
            len(self.predicted_trick_count)
            == len(self.actual_trick_count)
            == len(self.round_score)
        )
        if not same:
            raise ValueError("All score lists must have the same length")

        return self


class Scoreboard(pydantic.BaseModel):
    rounds: list[RoundScore] = pydantic.Field(default_factory=list)
