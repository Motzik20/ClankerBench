from clanker_bench.agents.agent import Agent
from clanker_bench.game.model.action import GameAction
from clanker_bench.game.model.gamestate import Observation
import random

class RandomAgent(Agent):
    def act(self, observation: Observation, action_space: tuple[GameAction, ...]) -> GameAction:
        rng = random.randint(0, len(action_space)-1)
        return action_space[rng]
