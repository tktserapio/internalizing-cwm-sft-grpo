import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple, Optional
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
SUITS = ['S', 'C', 'D', 'H']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
FACE_CARD_VALUE = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25
KNOCK_CARD_VALUE = 10

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = [rank + suit for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    player_hands = [deck[:10], deck[10:20]]
    stock_pile = deck[20:]
    discard_pile = [stock_pile.pop(0)]
    return {
        'player_hands': player_hands,
        'stock_pile': stock_pile,
        'discard_pile': discard_pile,
        'current_player': 0,
        'phase': 'Draw',
        'round_over': False,
        'scores': [0, 0],
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    current_player = new_state['current_player']
    if action.startswith("Draw"):
        if action == "Draw stock":
            card = new_state['stock_pile'].pop(0)
        elif action == "Draw upcard":
            card = new_state['discard_pile'].pop()
        new_state['player_hands'][current_player].append(card)
        new_state['phase'] = 'Discard'
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state['player_hands'][current_player].remove(card_to_discard)
        new_state['discard_pile'].append(card_to_discard)
        new_state['current_player'] = 1 - current_player
        new_state['phase'] = 'Draw'
    elif action == "Action: Knock":
        new_state['round_over'] = True
        # Handle scoring and end of round logic here
    elif action == "Pass":
        new_state['current_player'] = 1 - current_player
        if len(new_state['discard_pile']) == 1:
            new_state['phase'] = 'Draw'
        else:
            new_state['phase'] = 'Wall'
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
    # Calculate rewards based on the scoring rules
    # Placeholder for scoring logic
    return state['scores']

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['round_over']:
        return []
    if state['phase'] == 'Draw':
        return ["Draw stock", "Draw upcard"]
    elif state['phase'] == 'Discard':
        hand = state['player_hands'][state['current_player']]
        return [f"Action: {card}" for card in hand] + ["Action: Knock"]
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    obs = []
    for player_id in range(2):
        obs.append({
            'hand': state['player_hands'][player_id],
            'discard_pile': state['discard_pile'],
            'stock_size': len(state['stock_pile']),
            'current_player': state['current_player'],
            'phase': state['phase'],
        })
    return obs

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    return []

# Helper functions for scoring, determining melds, etc., would be added here.