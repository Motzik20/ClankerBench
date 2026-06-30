from clanker_bench.game.model.card import Card, Suit
from clanker_bench.game.model.gamestate import GameState, PlayedCard

def compute_demanded_suit(current_trick: list[PlayedCard]) -> Suit | None:
    for played in current_trick:
        if played.card.suit == Suit.CLANKER:
            continue
        elif played.card.suit == Suit.SINGULARITY:
            return None
        return played.card.suit
    return None

def get_allowed_suits(current_trick: list[PlayedCard], player_hand: list[Card]) -> set[Suit]:
    suits_in_hand: set[Suit] = {card.suit for card in player_hand}
    demanded_suit: Suit | None = compute_demanded_suit(current_trick)
    player_has_demanded_suit: bool = demanded_suit in suits_in_hand
    if player_has_demanded_suit and demanded_suit is not None:
        return {Suit.CLANKER, Suit.SINGULARITY, demanded_suit}
    else:
        return {suit for suit in Suit}

def is_legal_card_play(state: GameState, card: Card) -> bool:
    if card.suit not in get_allowed_suits(state.trick_state.current_trick, state.players[state.current_player].own_hand):
        return False
    return True
