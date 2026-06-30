import random

from clanker_bench.game.deck import init_deck, shuffle_deck, deal_cards, determine_trump
from clanker_bench.game.model.card import Card, Suit
from clanker_bench.game.model.config import Config
from clanker_bench.game.model.player_state import PlayerState
from clanker_bench.game.model.scoreboard import Scoreboard, RoundScore
from clanker_bench.game.model.gamestate import GameState, RoundState, TrickState

def new_game(config: Config, seed: int) -> GameState:
    rng: random.Random = random.Random(seed)
    initial_deck: list[Card] = init_deck()
    deck: list[Card] = shuffle_deck(initial_deck, rng)
    top_card, deck = deal_cards(1, deck)
    trump_suit, awaiting_trump_select = determine_trump(top_card.pop())
    player_states: list[PlayerState] = []
    for player in range(config.player_count):
        player_hand, deck = deal_cards(1, deck)
        player_state: PlayerState = PlayerState(
            player_id=player,
            name="Player {player + 1}",
            own_hand=player_hand
        )
        player_states.append(player_state)

    return GameState(
        round_nr=0,
        current_player=1,
        player_count=config.player_count,
        scoreboard=Scoreboard(),
        players=player_states,
        round_state=RoundState(
            current_trump_suit=trump_suit,
            awaiting_trump_select=awaiting_trump_select,
            predicted_player_tricks=[-1] * config.player_count,
            actual_player_tricks=[0] * config.player_count,
        ),
        trick_state=TrickState(starting_player=1),
    )
