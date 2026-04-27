import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

def shuffle_deck() -> List[int]:
    """Shuffles the deck and returns a list of card ranks."""
    suits = ['S', 'C', 'D', 'H']
    ranks = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def create_initial_state(deck: List[int]) -> State:
    """Creates the initial game state."""
    # Initial state variables
    player_0_cards = []
    player_1_cards = []
    upcard = None
    deadwood_0 = 0
    deadwood_1 = 0
    phase = "Draw"
    knock_card = 10  # Default knock card value
    player_0_melds = []
    player_1_melds = []

    # Distribute cards
    for i in range(len(deck)):
        if i % 2 == 0:
            player_0_cards.append(deck[i])
        else:
            player_1_cards.append(deck[i])

    return {
        "player_0_cards": player_0_cards,
        "player_1_cards": player_1_cards,
        "upcard": upcard,
        "deadwood_0": deadwood_0,
        "deadwood_1": deadwood_1,
        "phase": phase,
        "knock_card": knock_card,
        "player_0_melds": player_0_melds,
        "player_1_melds": player_1_melds,
        "deck": deck,
        "current_player": 0
    }

def is_terminal_state(state: State) -> bool:
    """Checks if the game is in a terminal state."""
    return state["phase"] == "Wall" or state["current_player"] == -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"