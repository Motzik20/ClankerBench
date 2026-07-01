from itertools import count

from clanker_bench.game.deck import shuffle_deck
from clanker_bench.game.model.action import GameAction, PredictTricksAction, PlayCardAction, SelectTrumpAction
from clanker_bench.game.model.card import Card, Suit
from clanker_bench.game.model.exception import IllegalActionException
from clanker_bench.game.model.gamestate import GameState, PlayedCard, TrickState, RoundState, Phase
from clanker_bench.game.model.scoreboard import RoundScore, Scoreboard
from clanker_bench.game.rules.play_card_rules import is_legal_card_play, compute_demanded_suit
from clanker_bench.game.rules.trump_selection_rules import is_legal_trump_select
from clanker_bench.game.setup import deal_round


def _is_trick_complete (state: GameState) -> bool:
    next_player = (state.trick_state.current_player + 1) % state.player_count
    return next_player == state.trick_state.starting_player

def _next_player(state: GameState) -> GameState:
    next_player = (state.trick_state.current_player + 1) % state.player_count
    new_state = state.model_copy()
    new_state.trick_state = state.trick_state.model_copy(update={"current_player": next_player})
    return new_state

def _remove_card_from_hand(card: Card, player_hand: list[Card]) -> list[Card]:
    t = count()
    return [c for c in player_hand if c != card or next(t) != 0]

def _play_card_to_trick(state: GameState, player_id: int, card: Card) -> GameState:
    new_state = state.model_copy()
    played_card: PlayedCard = PlayedCard(player_id=player_id, card=card)
    new_trick: list[PlayedCard] = [*state.trick_state.current_trick, played_card]
    new_state.trick_state = state.trick_state.model_copy(update={
        "current_trick": new_trick,
        "current_demanded_suit": compute_demanded_suit(new_trick),
    })
    player_hand: list[Card] = state.players[player_id].own_hand
    new_state.players[player_id].own_hand = _remove_card_from_hand(card, player_hand)
    return new_state


def _is_higher_card(new_card: Card, old_card: Card, trump_suit: Suit | None, demanded_suit: Suit | None) -> bool:
    suit_map = {Suit.SINGULARITY: 4, trump_suit: 3, demanded_suit: 2, Suit.CLANKER: 0}
    for suit in Suit:
        if suit == trump_suit or suit == demanded_suit or suit == Suit.CLANKER or suit == Suit.SINGULARITY:
            continue
        suit_map[suit] = 1

    if suit_map[new_card.suit] > suit_map[old_card.suit]:
        return True
    elif suit_map[new_card.suit] < suit_map[old_card.suit]:
        return False

    if new_card.rank > old_card.rank:
        return True

    return False


def _determine_trick_winner(state: GameState) -> int:
    current_trick = state.trick_state.current_trick
    demanded_suit = compute_demanded_suit(current_trick)
    highest_played_card = current_trick[0]
    for played in current_trick:
        if _is_higher_card(played.card, highest_played_card.card, state.round_state.current_trump_suit, demanded_suit):
            highest_played_card = played

    return highest_played_card.player_id



def _finish_trick(state: GameState) -> GameState:
    new_state: GameState = state.model_copy()
    winner: int = _determine_trick_winner(new_state)
    # move played cards into the game-wide history
    new_state.played_cards = [*state.round_state.played_cards, *state.trick_state.current_trick]
    # add win to trick count for actual winner
    new_state.round_state = state.round_state.model_copy(update={
        "actual_player_tricks": [
            count + 1 if player_id == winner else count
            for player_id, count in enumerate(state.round_state.actual_player_tricks)
        ],
    })
    # start a fresh trick led by the winner
    new_state.trick_state = TrickState(starting_player=winner, current_player=winner)
    new_state.round_state.trick_nr = state.round_state.trick_nr + 1
    return new_state


def _is_round_complete(new_state: GameState) -> bool:
    return new_state.round_state.trick_nr > new_state.round_nr


def _calculate_round_score(state: GameState) -> RoundScore:
    round_score = []
    round_state: RoundState = state.round_state
    predicted_player_tricks: list[int | None] = round_state.predicted_player_tricks
    if None in predicted_player_tricks:
        raise RuntimeError
    actual_player_tricks: list[int] = round_state.actual_player_tricks
    for player_id in range(state.player_count):
        if predicted_player_tricks[player_id] == actual_player_tricks[player_id]:
            round_score.append(20 + actual_player_tricks[player_id] * 10)
        else:
            round_score.append(-abs(predicted_player_tricks[player_id] - actual_player_tricks[player_id]) * 10)

    new_score: RoundScore = RoundScore(
        predicted_trick_count=state.round_state.predicted_player_tricks,
        actual_trick_count=state.round_state.actual_player_tricks,
        round_score=round_score,
    )
    return new_score


def _finish_round(state: GameState) -> GameState:
    score: RoundScore = _calculate_round_score(state)
    scoreboard = state.scoreboard.model_copy(
        update={"rounds": [*state.scoreboard.rounds, score]})
    if state.round_nr + 1 >= state.round_count:
        return state.model_copy(update={"scoreboard": scoreboard, "phase": Phase.FINISHED})
    return deal_round(
        seed=state.seed,
        round_nr=state.round_nr + 1,
        dealer_id=(state.dealer_id + 1) % state.player_count,
        player_count=state.player_count,
        scoreboard=scoreboard,
    )


def _apply_play_card_action(state: GameState, action: PlayCardAction) -> GameState:
    if not is_legal_card_play(state, action.card):
        raise IllegalActionException(f"Action to play the {action.card} is not legal!")

    new_state = _play_card_to_trick(state, state.trick_state.current_player, action.card)
    if not _is_trick_complete(new_state):
        return _next_player(new_state)

    new_state = _finish_trick(new_state)
    if not _is_round_complete(new_state):
        return new_state
    return _finish_round(new_state)


def _apply_select_trump_action(state: GameState, action: SelectTrumpAction) -> GameState:
    new_state = state.model_copy()
    if not is_legal_trump_select(state, action.suit):
        raise IllegalActionException(f"Action to select trump {action.suit} is not legal!")
    new_state.round_state = state.round_state.model_copy(update={
        "current_trump_suit": action.suit,
        "awaiting_trump_select": False,
    })
    return new_state

def _apply_predict_action(state: GameState, action: GameAction) -> GameState:
    pass

def step(state: GameState, action: GameAction) -> GameState:
    match action:
        case SelectTrumpAction() if state.phase is Phase.SELECT_TRUMP:
            return _apply_select_trump_action(state, action)
        case PredictTricksAction() if state.phase is Phase.PREDICT:
            return _apply_predict_action(state, action)
        case PlayCardAction() if state.phase is Phase.PLAY:
            return _apply_play_card_action(state, action)
        case _:
            raise IllegalActionException(f"{type(action).__name__} nicht erlaubt in Phase {state.phase}")