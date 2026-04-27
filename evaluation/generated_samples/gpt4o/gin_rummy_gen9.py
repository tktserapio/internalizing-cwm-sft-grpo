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
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
DECK = [rank + suit for suit in SUITS for rank in RANKS]
KNOCK_THRESHOLD = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = DECK[:]
    random.shuffle(deck)
    hands = [deck[:10], deck[10:20]]
    stock_pile = deck[20:-1]
    upcard = deck[-1]
    
    return {
        'hands': hands,
        'stock_pile': stock_pile,
        'upcard': upcard,
        'phase': 'Draw',
        'current_player': 0,
        'scores': [0, 0],
        'round_over': False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    
    if action.startswith("Draw"):
        new_state = handle_draw_action(new_state, action)
    elif action.startswith("Action:"):
        new_state = handle_discard_or_knock_action(new_state, action)
    elif action == "Pass":
        new_state = handle_pass_action(new_state)
    
    return new_state

def handle_draw_action(state: State, action: Action) -> State:
    """Handles draw actions and updates the state accordingly."""
    player = state['current_player']
    if action == "Draw stock":
        card = state['stock_pile'].pop()
    elif action == "Draw upcard":
        card = state['upcard']
        state['upcard'] = None
    
    state['hands'][player].append(card)
    state['phase'] = 'Discard'
    return state

def handle_discard_or_knock_action(state: State, action: Action) -> State:
    """Handles discard and knock actions."""
    player = state['current_player']
    if action.startswith("Action: Knock"):
        state = handle_knock(state)
    else:
        card = action.split(": ")[1]
        state['hands'][player].remove(card)
        state['upcard'] = card
        state['phase'] = 'Draw'
        state['current_player'] = 1 - player
    return state

def handle_knock(state: State) -> State:
    """Handles the knock action and calculates scores."""
    # Implement knock logic and scoring
    state['round_over'] = True
    return state

def handle_pass_action(state: State) -> State:
    """Handles the pass action."""
    state['current_player'] = 1 - state['current_player']
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state['round_over'] else state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['round_over']:
        return state['scores']
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['round_over']:
        return []
    
    player = state['current_player']
    if state['phase'] == 'Draw':
        actions = ["Draw stock"]
        if state['upcard']:
            actions.append("Draw upcard")
        return actions
    elif state['phase'] == 'Discard':
        actions = [f"Action: {card}" for card in state['hands'][player]]
        if calculate_deadwood(state['hands'][player]) <= KNOCK_THRESHOLD:
            actions.append("Action: Knock")
        return actions
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {'hand': state['hands'][0], 'upcard': state['upcard'], 'phase': state['phase']},
        {'hand': state['hands'][1], 'upcard': state['upcard'], 'phase': state['phase']}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # Implement resampling logic
    return []

def calculate_deadwood(hand: List[str]) -> int:
    """Calculates the deadwood points in a hand."""
    # Implement deadwood calculation
    return 0