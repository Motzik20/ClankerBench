from clanker_bench.agents.agent import Agent
from clanker_bench.game.model.action import GameAction
from clanker_bench.game.model.gamestate import Observation
import random

class RandomAgent(Agent):
    def act(self, observation: Observation, legal_actions: list[GameAction]) -> GameAction:
        rng = random.randint(0, len(legal_actions)-1)
        return legal_actions[rng]
