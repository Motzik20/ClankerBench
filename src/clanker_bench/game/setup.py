import random

from clanker_bench.game.deck import init_deck, shuffle_deck, deal_cards, determine_trump
from clanker_bench.game.model.card import Card, Suit
from clanker_bench.game.model.config import Config
from clanker_bench.game.model.player_state import PlayerState
from clanker_bench.game.model.scoreboard import Scoreboard, RoundScore
from clanker_bench.game.model.gamestate import GameState, RoundState, TrickState, Phase


def _round_rng(seed: int, round_nr: int) -> random.Random:
    return random.Random(f"{seed}:{round_nr}")

def deal_round(
    seed: int,
    round_nr: int,
    dealer_id: int,
    player_count: int,
    scoreboard: Scoreboard
) -> GameState:
    initial_deck: list[Card] = init_deck()
    rng = _round_rng(seed, round_nr)
    shuffled_deck: list[Card] = shuffle_deck(initial_deck, rng)
    top_card, deck = deal_cards(1, shuffled_deck)
    trump_suit, awaiting_trump_select = determine_trump(top_card.pop())
    round_count = (len(deck) + 1) // player_count
    player_states: list[PlayerState] = []
    for player_id in range(player_count):
        player_hand, deck = deal_cards(round_nr + 1, deck)
        player_state: PlayerState = PlayerState(
            player_id=player_id,
            name=f"Player {player_id + 1}",
            own_hand=player_hand
        )
        player_states.append(player_state)

    starting = (dealer_id + 1) % player_count
    return GameState(
        seed=seed,
        phase= Phase.SELECT_TRUMP if awaiting_trump_select else Phase.PREDICT,
        round_nr=0,
        round_count=round_count,
        dealer_id=dealer_id,
        player_count=player_count,
        scoreboard=Scoreboard(),
        players=player_states,
        round_state=RoundState(
            current_trump_suit=trump_suit,
            predicted_player_tricks=[-1] * player_count,
            actual_player_tricks=[0] * player_count,
        ),
        trick_state=TrickState(starting_player=starting, current_player=starting),
    )


def new_game(config: Config, seed: int) -> GameState:
    return deal_round(seed, round_nr=0, dealer_id=0,
                      player_count=config.player_count, scoreboard=Scoreboard())
