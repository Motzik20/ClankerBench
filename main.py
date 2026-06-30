# This is a sample Python script.
from clanker_bench.game.model.config import Config
from clanker_bench.game.setup import new_game

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    config = Config()
    State = new_game(config, 1)
    
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
