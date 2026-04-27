import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple, Dict
import random

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
SUITS = ['S', 'C', 'D', 'H']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
KNOCK_THRESHOLD = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = [rank + suit for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return {
        'deck': deck,
        'discard_pile': [],
        'hands': [deck[:10], deck[10:20]],
        'current_player': 0,
        'phase': 'Draw',
        'knock_card': KNOCK_THRESHOLD,
        'scores': [0, 0],
        'terminal': False
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
    new_state = state.copy()
    if action == "Draw stock":
        card = new_state['deck'].pop()
        new_state['hands'][new_state['current_player']].append(card)
    elif action == "Draw upcard":
        card = new_state['discard_pile'].pop()
        new_state['hands'][new_state['current_player']].append(card)
    new_state['phase'] = 'Discard'
    return new_state

def handle_discard_or_knock_action(state: State, action: Action) -> State:
    """Handles discard or knock actions and updates the state accordingly."""
    new_state = state.copy()
    if action.startswith("Action: Knock"):
        new_state = handle_knock_action(new_state)
    else:
        card = action.split(": ")[1]
        new_state['hands'][new_state['current_player']].remove(card)
        new_state['discard_pile'].append(card)
        new_state['current_player'] = 1 - new_state['current_player']
        new_state['phase'] = 'Draw'
    return new_state

def handle_knock_action(state: State) -> State:
    """Handles the knock action and transitions the state to terminal."""
    new_state = state.copy()
    # Calculate deadwood and determine if it's a valid knock
    # Implement scoring logic
    new_state['terminal'] = True
    return new_state

def handle_pass_action(state: State) -> State:
    """Handles the pass action during the initial upcard decision."""
    new_state = state.copy()
    new_state['current_player'] = 1 - new_state['current_player']
    if not new_state['discard_pile']:
        new_state['phase'] = 'Draw'
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state['terminal'] else state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['terminal']:
        # Calculate rewards based on the final state
        return state['scores']
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['terminal']:
        return []
    if state['phase'] == 'Draw':
        actions = ["Draw stock"]
        if state['discard_pile']:
            actions.append("Draw upcard")
        return actions
    elif state['phase'] == 'Discard':
        hand = state['hands'][state['current_player']]
        actions = [f"Action: {card}" for card in hand]
        if calculate_deadwood(hand) <= state['knock_card']:
            actions.append("Action: Knock")
        return actions
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
    # Implement logic to reconstruct a valid action sequence
    return []

def calculate_deadwood(hand: List[str]) -> int:
    """Calculates the deadwood points in a player's hand."""
    # Implement deadwood calculation logic
    return 0

# Helper functions for melds, scoring, etc., can be added here.