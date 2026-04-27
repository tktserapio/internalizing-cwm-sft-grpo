import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
SUITS = ['S', 'C', 'D', 'H']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
DECK = [rank + suit for suit in SUITS for rank in RANKS]
KNOCK_CARD_VALUE = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = DECK[:]
    random.shuffle(deck)
    hands = [deck[:10], deck[10:20]]
    stock_pile = deck[20:]
    discard_pile = [stock_pile.pop(0)]
    return {
        'hands': hands,
        'stock_pile': stock_pile,
        'discard_pile': discard_pile,
        'current_player': 0,
        'phase': 'Draw',
        'scores': [0, 0]
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    current_player = new_state['current_player']

    if action.startswith("Draw"):
        if action == "Draw stock":
            new_state['hands'][current_player].append(new_state['stock_pile'].pop(0))
        elif action == "Draw upcard":
            new_state['hands'][current_player].append(new_state['discard_pile'].pop())
        new_state['phase'] = 'Discard'
    elif action.startswith("Action: "):
        card = action.split(": ")[1]
        new_state['hands'][current_player].remove(card)
        new_state['discard_pile'].append(card)
        new_state['current_player'] = 1 - current_player
        new_state['phase'] = 'Draw'
    elif action == "Action: Knock":
        # Handle knock logic
        pass
    elif action == "Pass":
        new_state['current_player'] = 1 - current_player

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['phase'] == 'Wall':
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    return state['scores']

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['phase'] == 'Wall':
        return []
    current_player = state['current_player']
    if state['phase'] == 'Draw':
        return ["Draw stock", "Draw upcard"]
    elif state['phase'] == 'Discard':
        hand = state['hands'][current_player]
        return [f"Action: {card}" for card in hand] + ["Action: Knock"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {'hand': state['hands'][0], 'discard_pile': state['discard_pile']},
        {'hand': state['hands'][1], 'discard_pile': state['discard_pile']}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function would require a more complex implementation to simulate a valid history.
    # For now, we will return an empty list as a placeholder.
    return []

# Helper functions can be added here to manage melds, scoring, etc.