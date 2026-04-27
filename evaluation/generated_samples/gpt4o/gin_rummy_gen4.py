import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple
import random

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
    deck = DECK.copy()
    random.shuffle(deck)
    player_hands = [deck[:10], deck[10:20]]
    stock_pile = deck[20:]
    discard_pile = []
    current_player = 0
    phase = 'Draw'
    
    return {
        'player_hands': player_hands,
        'stock_pile': stock_pile,
        'discard_pile': discard_pile,
        'current_player': current_player,
        'phase': phase,
        'scores': [0, 0],
        'round_over': False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player = new_state['current_player']
    hand = new_state['player_hands'][player]
    
    if action == "Draw stock":
        card = new_state['stock_pile'].pop()
        hand.append(card)
        new_state['phase'] = 'Discard'
    elif action == "Draw upcard":
        card = new_state['discard_pile'].pop()
        hand.append(card)
        new_state['phase'] = 'Discard'
    elif action.startswith("Action: "):
        card = action.split(": ")[1]
        hand.remove(card)
        new_state['discard_pile'].append(card)
        new_state['current_player'] = 1 - player
        new_state['phase'] = 'Draw'
    elif action == "Action: Knock":
        new_state['round_over'] = True
        # Handle scoring and end of round logic
    elif action == "Pass":
        new_state['current_player'] = 1 - player
    
    return new_state

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
    return state['scores']

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['round_over']:
        return []
    
    player = state['current_player']
    phase = state['phase']
    hand = state['player_hands'][player]
    legal_actions = []
    
    if phase == 'Draw':
        if state['stock_pile']:
            legal_actions.append("Draw stock")
        if state['discard_pile']:
            legal_actions.append("Draw upcard")
    elif phase == 'Discard':
        legal_actions.extend([f"Action: {card}" for card in hand])
        if calculate_deadwood(hand) <= KNOCK_THRESHOLD:
            legal_actions.append("Action: Knock")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            'hand': state['player_hands'][0],
            'discard_pile': state['discard_pile'],
            'stock_size': len(state['stock_pile']),
            'phase': state['phase']
        },
        {
            'hand': state['player_hands'][1],
            'discard_pile': state['discard_pile'],
            'stock_size': len(state['stock_pile']),
            'phase': state['phase']
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function would require a more complex implementation to reconstruct the history
    return []

def calculate_deadwood(hand: List[str]) -> int:
    """Calculates the deadwood value of a hand."""
    # Implement deadwood calculation logic
    return 0

# Note: This implementation is a starting point and does not cover all game rules and logic.