import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def shuffle_deck() -> List[int]:
    """Shuffles a standard 52-card deck."""
    suits = ['S', 'C', 'D', 'H']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = [(rank + suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def create_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state setup
    state = {
        'deck': shuffle_deck(),
        'upcard': None,
        'dealer': 0,  # Dealer starts as player 0
        'phase': 'Draw',
        'knock_card': 10,  # Default knock card value
        'player_0_hand': [],
        'player_1_hand': [],
        'player_0_deadwood': 0,
        'player_1_deadwood': 0,
        'player_0_melds': [],
        'player_1_melds': [],
        'player_0_meld_count': 0,
        'player_1_meld_count': 0,
        'player_0_score': 0,
        'player_1_score': 0,
        'wall': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    
    if action == 'Draw stock':
        if len(state['deck']) > 0:
            new_state['player_0_hand'].append(state['deck'].pop())
            new_state['player_1_hand'].append(state['deck'].pop())
            new_state['phase'] = 'Discard'
        else:
            new_state['phase'] = 'Wall'
    elif action == 'Draw upcard':
        if state['upcard'] is None:
            new_state['upcard'] = state['deck'].pop()
            new_state['phase'] = 'Discard'
        else:
            new_state['phase'] = 'Draw'
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        if card_to_discard in state['player_0_hand']:
            new_state['player_0_hand'].remove(card_to_discard)
            new_state['wall'].append(card_to_discard)
            new_state['phase'] = 'Discard'
        else:
            new_state['phase'] = 'Wall'
    elif action == 'Action: Knock':
        if new_state['player_0_deadwood'] <= new_state['knock_card']:
            new_state['phase'] = 'Layoff'
            new_state['player_0_melds'], new_state['player_0_deadwood'] = new_state['player_0_melds'], 0
            new_state['player_1_melds'], new_state['player_1_deadwood'] = new_state['player_1_melds'], 0
        else:
            new_state['phase'] = 'Wall'
    elif action == 'Action: Done':
        new_state['phase'] = 'Wall'
    elif action == 'Pass':
        new_state['phase'] = 'Wall'
    else:
        raise ValueError(f"Invalid action: {action}")
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['phase'] == 'Wall':
        return -4
    return state['dealer']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['phase'] == 'Wall':
        return [state['player_0_score'], state['player_1_score']]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['phase'] == 'Wall':
        return []
    elif state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    elif state['phase'] == 'Discard':
        if state['upcard'] is None:
            return ['Draw stock']
        else:
            return ['Draw stock', 'Draw upcard']
    elif state['phase'] == 'Layoff':
        return ['Action: Knock', 'Action: Done']
    else:
        raise ValueError("Invalid phase")

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'phase': state['phase'],
        'upcard': state['upcard'],
        'deck': state['deck'],
        'dealer': state['dealer'],
        'knock_card': state['knock_card'],
        'player_0_hand': state['player_0_hand'],
        'player_1_hand': state['player_1_hand'],
        'player_0_deadwood': state['player_0_deadwood'],
        'player_1_deadwood': state['player_1_deadwood'],
        'player_0_melds': state['player_0_melds'],
        'player_1_melds': state['player_1_melds'],
        'player_0_meld_count': state['player_0_meld_count'],
        'player_1_meld_count': state['player_1_meld_count'],
        'wall': state['wall']
    }
    player_1_obs = {
        'phase': state['phase'],
        'upcard': state['upcard'],
        'deck': state['deck'],
        'dealer': state['dealer'],
        'knock_card': state['knock_card'],
        'player_0_hand': state['player_1_hand'],
        'player_1_hand': state['player_0_hand'],
        'player_0_deadwood': state['player_1_deadwood'],
        'player_1_deadwood': state['player_0_deadwood'],
        'player_0_melds': state['player_1_melds'],
        'player_1_melds': state['player_0_melds'],
        'player_0_meld_count': state['player_1_meld_count'],
        'player_1_meld_count': state['player_0_meld_count'],
        'wall': state['wall']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ['Draw stock', 'Action: 3d', 'Action: Knock']
    else:
        return ['Draw stock', 'Action: 3d', 'Action: Knock']