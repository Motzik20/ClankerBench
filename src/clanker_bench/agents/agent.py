from abc import ABC, abstractmethod

from clanker_bench.game.model.action import GameAction
from clanker_bench.game.model.gamestate import Observation


class Agent(ABC):
    @abstractmethod
    def act(
        self, observation: Observation, action_space: tuple[GameAction, ...],
    ) -> GameAction:
        pass
