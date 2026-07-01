import random
from typing import Sequence

from clanker_bench.game.model.card import Card, Suit

def shuffle_deck(cards: Sequence[Card], rng: random.Random) -> list[Card]:
    shuffled_deck = list(cards)
    rng.shuffle(shuffled_deck)
    return shuffled_deck


def init_deck() -> list[Card]:
    cards: list[Card] = []
    for (suit) in Suit:
        if suit == Suit.CLANKER or suit == Suit.SINGULARITY:
            cards.extend([Card(suit=suit)] * 4)
            continue
        for rank in range(13):
            cards.append(Card(suit=suit, rank=rank + 1))
    return cards

def deal_cards(current_round: int, deck: list[Card]) -> tuple[list[Card], list[Card]]:
    dealt = deck[:current_round]
    remaining = deck[current_round:]
    return dealt, remaining

def determine_trump(card: Card) -> tuple[None | Suit, bool]:
    if card.suit == Suit.CLANKER:
        return None, False
    elif card.suit == Suit.SINGULARITY:
        return None, True
    else:
        return card.suit, False

