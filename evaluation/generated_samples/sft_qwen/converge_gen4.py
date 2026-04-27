import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to create a deep copy of the state
def deepcopy_state(state):
    return copy.deepcopy(state)

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial positions for Blue (Player 0) and Red (Player 1)
    blue_units = [(0, 0), (0, 4)]
    red_units = [(4, 0), (4, 4)]
    center_square = (2, 2)
    
    return {
        'blue_units': blue_units,
        'red_units': red_units,
        'current_player': 0,  # Player 0 starts
        'turn_count': 0,
        'center_square_occupied': False,
        'stunned_units': [],
        'state': 'active'
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = deepcopy_state(state)
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2  # Switch to other player
        return new_state
    
    # Parse the action
    source, target = action.split(' to ')
    sr, sc = map(int, source.split(','))
    tr, tc = map(int, target.split(','))
    
    # Check if the action is valid
    if (sr, sc) not in state['blue_units'] and (sr, sc) not in state['red_units']:
        raise ValueError("Invalid source position")
    if (tr, tc) in state['blue_units'] or (tr, tc) in state['red_units']:
        raise ValueError("Target position is occupied")
    
    # Apply the action
    if (sr, sc) in state['blue_units']:
        new_state['blue_units'].remove((sr, sc))
        new_state['blue_units'].append((tr, tc))
    elif (sr, sc) in state['red_units']:
        new_state['red_units'].remove((sr, sc))
        new_state['red_units'].append((tr, tc))
    
    # Check for stun
    for unit in state['blue_units'] + state['red_units']:
        if abs(unit[0] - tr) <= 1 and abs(unit[1] - tc) <= 1:
            new_state['stunned_units'].append(unit)
            break
    
    # Update turn count
    new_state['turn_count'] += 1
    
    # Check if the center square is occupied
    if (2, 2) in state['blue_units']:
        new_state['state'] = 'win'
    elif (2, 2) in state['red_units']:
        new_state['state'] = 'win'
    
    # Check if the game is over
    if new_state['state'] != 'active' or new_state['turn_count'] >= 50:
        new_state['state'] = 'draw'
    
    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    if state['state'] in ['win', 'draw']:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    if state['state'] == 'win':
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    elif state['state'] == 'draw':
        return [0.5, 0.5]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    if state['state'] != 'active':
        return legal_actions
    
    for unit in state['blue_units'] + state['red_units']:
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nr, nc = unit[0] + dr, unit[1] + dc
            if 0 <= nr <= 4 and 0 <= nc <= 4 and (nr, nc) not in state['blue_units'] + state['red_units']:
                legal_actions.append(f'move ({unit[0]}, {unit[1]}) to ({nr}, {nc})')
    
    if not legal_actions:
        legal_actions.append('pass')
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {
        'board': state['blue_units'] + state['red_units'],
        'current_player': state['current_player']
    }
    player_1_obs = {
        'board': state['blue_units'] + state['red_units'],
        'current_player': state['current_player']
    }
    return [player_0_obs, player_1_obs]