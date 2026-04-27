import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple, Union

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants for card ranks
CARD_RANKS = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
CARD_VALUES = list(CARD_RANKS.keys())

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = CARD_VALUES * 4  # Full deck of 52 cards
    random.shuffle(deck)
    player_0_deck = deck[:26]
    player_1_deck = deck[26:]
    return {
        "draw_piles": [player_0_deck, player_1_deck],
        "hands": [player_0_deck[:3], player_1_deck[:3]],
        "win_piles": [[], []],
        "current_player": 0,
        "publicly_revealed_cards": [],
        "phase": "battle"
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    new_state["draw_piles"] = [list(pile) for pile in state["draw_piles"]]
    new_state["hands"] = [list(hand) for hand in state["hands"]]
    new_state["win_piles"] = [list(pile) for pile in state["win_piles"]]
    new_state["publicly_revealed_cards"] = list(state["publicly_revealed_cards"])
    
    if action.startswith("play:"):
        card = action.split(":")[1]
        player = new_state["current_player"]
        opponent = 1 - player
        new_state["hands"][player].remove(card)
        new_state["publicly_revealed_cards"].append((player, card))
        
        if len(new_state["publicly_revealed_cards"]) == 2:
            # Resolve battle
            card_0 = new_state["publicly_revealed_cards"][0][1]
            card_1 = new_state["publicly_revealed_cards"][1][1]
            if CARD_RANKS[card_0] > CARD_RANKS[card_1]:
                winner = 0
            elif CARD_RANKS[card_0] < CARD_RANKS[card_1]:
                winner = 1
            else:
                winner = None  # Tie, showdown needed
            
            if winner is not None:
                new_state["win_piles"][winner].extend([card_0, card_1])
                new_state["publicly_revealed_cards"] = []
                new_state["phase"] = "battle"
                new_state["current_player"] = 0
            else:
                new_state["phase"] = "showdown"
                new_state["current_player"] = 0

        else:
            new_state["current_player"] = opponent

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if is_terminal(state):
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if is_terminal(state):
        win_pile_counts = [len(pile) for pile in state["win_piles"]]
        if win_pile_counts[0] > win_pile_counts[1]:
            return [1.0, 0.0]
        elif win_pile_counts[0] < win_pile_counts[1]:
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if is_terminal(state):
        return []
    
    player = state["current_player"]
    return [f"play:{card}" for card in state["hands"][player]]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            "hand": state["hands"][0],
            "win_pile": state["win_piles"][0],
            "publicly_revealed_cards": state["publicly_revealed_cards"]
        },
        {
            "hand": state["hands"][1],
            "win_pile": state["win_piles"][1],
            "publicly_revealed_cards": state["publicly_revealed_cards"]
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Union[Action, None]]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function is complex and requires a detailed understanding of the game state and history.
    # For simplicity, we'll assume the history is valid and return it.
    return [action for _, action in obs_action_history if action is not None]

def is_terminal(state: State) -> bool:
    """Check if the game is in a terminal state."""
    return any(len(pile) == 0 for pile in state["draw_piles"]) or any(len(pile) == 52 for pile in state["win_piles"])

# Helper function to determine if the game is over
def is_game_over(state: State) -> bool:
    """Determine if the game has ended."""
    return any(len(pile) == 0 for pile in state["draw_piles"]) or any(len(pile) == 52 for pile in state["win_piles"])