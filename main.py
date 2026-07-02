# This is a sample Python script.
from clanker_bench.agents.agent import Agent
from clanker_bench.agents.random_agent import RandomAgent
from clanker_bench.game.setup import new_game
from clanker_bench.runner.run import play_game

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    random_agents: list[Agent] = [RandomAgent() for i in range(3)]
    play_game(random_agents, 0)

    
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
