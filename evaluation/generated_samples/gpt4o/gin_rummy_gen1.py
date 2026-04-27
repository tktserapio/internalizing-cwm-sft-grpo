import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
SUITS = ['S', 'C', 'D', 'H']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
DECK = [rank + suit for suit in SUITS for rank in RANKS]
KNOCK_CARD_VALUE = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25

# Helper functions
def calculate_deadwood(hand: List[str]) -> int:
    """Calculate the deadwood value of a hand."""
    deadwood_value = 0
    for card in hand:
        rank = card[:-1]
        if rank in ['J', 'Q', 'K']:
            deadwood_value += 10
        elif rank == 'A':
            deadwood_value += 1
        else:
            deadwood_value += int(rank)
    return deadwood_value

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    random.shuffle(DECK)
    player_hands = [DECK[:10], DECK[10:20]]
    stock_pile = DECK[20:]
    discard_pile = []
    return {
        'phase': 'Draw',
        'current_player': 0,
        'player_hands': player_hands,
        'stock_pile': stock_pile,
        'discard_pile': discard_pile,
        'scores': [0, 0]
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    current_player = new_state['current_player']
    if action == "Draw stock":
        card = new_state['stock_pile'].pop(0)
        new_state['player_hands'][current_player].append(card)
        new_state['phase'] = 'Discard'
    elif action == "Draw upcard":
        card = new_state['discard_pile'].pop()
        new_state['player_hands'][current_player].append(card)
        new_state['phase'] = 'Discard'
    elif action.startswith("Action: "):
        card = action.split(": ")[1]
        new_state['player_hands'][current_player].remove(card)
        new_state['discard_pile'].append(card)
        new_state['phase'] = 'Draw'
        new_state['current_player'] = 1 - current_player
    elif action == "Action: Knock":
        # Handle knocking logic
        pass
    elif action == "Pass":
        # Handle pass logic
        pass
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
    elif state['phase'] == 'Draw':
        actions = ["Draw stock"]
        if state['discard_pile']:
            actions.append("Draw upcard")
        return actions
    elif state['phase'] == 'Discard':
        hand = state['player_hands'][state['current_player']]
        actions = [f"Action: {card}" for card in hand]
        if calculate_deadwood(hand) <= KNOCK_CARD_VALUE:
            actions.append("Action: Knock")
        return actions
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            'hand': state['player_hands'][0],
            'discard_pile': state['discard_pile'],
            'phase': state['phase']
        },
        {
            'hand': state['player_hands'][1],
            'discard_pile': state['discard_pile'],
            'phase': state['phase']
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function would require a more complex implementation to simulate a valid history.
    return []

# Note: The implementation of knocking, scoring, and handling the end of the game is not fully detailed here.
# Further development is needed to handle these aspects according to the game rules.