from typing import TYPE_CHECKING

from clanker_bench.agents.agent import Agent
from clanker_bench.game.engine import active_player, get_action_space, observe, step
from clanker_bench.game.model.config import Config
from clanker_bench.game.model.gamestate import GameState, Observation, Phase
from clanker_bench.game.model.scoreboard import Scoreboard
from clanker_bench.game.setup import new_game
from clanker_bench.render import render

if TYPE_CHECKING:
    from clanker_bench.game.model.action import GameAction


def play_game(agents: list[Agent], seed: int) -> Scoreboard:
    config: Config = Config(player_count=len(agents))
    game_state: GameState = new_game(config, seed=seed)
    while game_state.phase != Phase.FINISHED:
        action_space: tuple[GameAction, ...] = get_action_space(game_state)
        actor: int = active_player(game_state)
        agent: Agent = agents[actor]
        observation: Observation = observe(game_state, actor)
        action: GameAction = agent.act(observation, action_space)
        game_state: GameState = step(game_state, action)
        print(render(game_state))
    return game_state.scoreboard
