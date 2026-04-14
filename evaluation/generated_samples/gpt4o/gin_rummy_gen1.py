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
FACE_CARD_VALUE = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25
KNOCK_CARD_VALUE = 10

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = [rank + suit for suit in SUITS for rank in RANKS]
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
        'round_over': False,
        'scores': [0, 0]
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action.startswith('Draw'):
        handle_draw_action(new_state, action)
    elif action.startswith('Action:'):
        handle_discard_or_knock_action(new_state, action)
    elif action == 'Pass':
        handle_pass_action(new_state)
    return new_state

def handle_draw_action(state: State, action: Action):
    """Handles the draw action."""
    if action == 'Draw stock':
        card = state['stock_pile'].pop(0)
    elif action == 'Draw upcard':
        card = state['discard_pile'].pop()
    state['hands'][state['current_player']].append(card)
    state['phase'] = 'Discard'

def handle_discard_or_knock_action(state: State, action: Action):
    """Handles the discard or knock action."""
    if action == 'Action: Knock':
        state['round_over'] = True
    else:
        card = action.split(': ')[1]
        state['hands'][state['current_player']].remove(card)
        state['discard_pile'].append(card)
        state['current_player'] = 1 - state['current_player']
        state['phase'] = 'Draw'

def handle_pass_action(state: State):
    """Handles the pass action."""
    state['current_player'] = 1 - state['current_player']

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state['round_over'] else state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state['round_over']:
        return [0.0, 0.0]
    # Calculate rewards based on deadwood and bonuses
    return calculate_rewards(state)

def calculate_rewards(state: State) -> List[float]:
    """Calculate the rewards at the end of a round."""
    # Placeholder for reward calculation logic
    return [0.0, 0.0]  # Implement scoring logic here

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['round_over']:
        return []
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    elif state['phase'] == 'Discard':
        hand = state['hands'][state['current_player']]
        return [f"Action: {card}" for card in hand] + ['Action: Knock']
    return []

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
    # Placeholder for resampling logic
    return []  # Implement resampling logic here

# Helper functions to manage game logic can be added here