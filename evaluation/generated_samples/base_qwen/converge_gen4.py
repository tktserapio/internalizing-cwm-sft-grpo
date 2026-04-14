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

# Helper function to check if a given position is within the board boundaries
def is_within_bounds(pos):
    return 0 <= pos[0] <= 4 and 0 <= pos[1] <= 4

# Initial state setup
def get_initial_state() -> State:
    # Player 0 (Blue) starts with two units at (0, 0) and (0, 4)
    blue_units = [(0, 0), (0, 4)]
    # Player 1 (Red) starts with two units at (4, 0) and (4, 4)
    red_units = [(4, 0), (4, 4)]
    return {
        'blue_units': blue_units,
        'red_units': red_units,
        'current_player': 0,
        'turn_count': 0,
        'center_square_occupied': False
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    
    # Parse the action
    source, target = action.split(' to ')
    sr, sc = map(int, source.split(','))
    tr, tc = map(int, target.split(','))
    
    # Check if the source and target positions are valid
    if not is_within_bounds((sr, sc)) or not is_within_bounds((tr, tc)):
        raise ValueError("Invalid move")
    
    # Update the source unit's position
    for i, unit in enumerate(new_state['blue_units']):
        if unit == (sr, sc):
            new_state['blue_units'][i] = (tr, tc)
            break
    
    # Check if the center square is now occupied
    if (2, 2) in new_state['blue_units']:
        new_state['center_square_occupied'] = True
    
    # Update the turn count
    new_state['turn_count'] += 1
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    # Check for stun mechanic
    for unit in new_state['blue_units']:
        if (unit[0], unit[1]) in [(sr, sc)]:
            new_state['blue_units'].append(unit)
            new_state['blue_units'].remove(unit)
            break
    
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Blue' if player_id == 0 else 'Red'

# Get rewards
def get_rewards(state: State) -> list[float]:
    if state['center_square_occupied']:
        return [1.0, 0.0]
    elif state['turn_count'] >= 50:
        return [0.5, 0.5]
    else:
        return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    for unit in state['blue_units']:
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            new_pos = (unit[0] + dr, unit[1] + dc)
            if is_within_bounds(new_pos) and new_pos not in state['blue_units'] and new_pos not in state['red_units']:
                legal_actions.append(f'move {unit} to {new_pos}')
    if not legal_actions and state['current_player'] != 0:
        legal_actions.append('pass')
    return legal_actions

# Get observations
def get_observations(state: State) -> list[PlayerObservation]:
    blue_units = state['blue_units']
    red_units = state['red_units']
    return [
        {'units': blue_units, 'stunned_units': []},
        {'units': red_units, 'stunned_units': []}
    ]