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

# Helper function to check if a position is within the board boundaries
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

# Apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    
    # Parse the action string
    src_pos, dest_pos = action.split(' to ')
    src_pos = tuple(map(int, src_pos.split(',')))
    dest_pos = tuple(map(int, dest_pos.split(',')))
    
    # Check if the source position is valid
    if not is_within_bounds(src_pos):
        raise ValueError(f"Invalid source position {src_pos}")
    
    # Check if the destination position is valid
    if not is_within_bounds(dest_pos):
        raise ValueError(f"Invalid destination position {dest_pos}")
    
    # Check if the source position is occupied by the current player
    if src_pos not in state[f'blue_units' if state['current_player'] == 0 else 'red_units']:
        raise ValueError("Source position is not occupied by the current player")
    
    # Check if the destination position is empty
    if dest_pos in state[f'blue_units' if state['current_player'] == 0 else 'red_units']:
        raise ValueError("Destination position is already occupied")
    
    # Move the unit
    if state['current_player'] == 0:
        new_state[f'blue_units'].remove(src_pos)
        new_state[f'blue_units'].append(dest_pos)
    else:
        new_state[f'red_units'].remove(src_pos)
        new_state[f'red_units'].append(dest_pos)
    
    # Update the current player
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    # Check if the center square is occupied
    if dest_pos == (2, 2):
        new_state['center_square_occupied'] = True
    
    # Increment the turn count
    new_state['turn_count'] += 1
    
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Blue' if player_id == 0 else 'Red'

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    if state['center_square_occupied']:
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    elif state['turn_count'] >= 50:
        return [0.5, 0.5]
    else:
        return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    if state['current_player'] == 0:
        blue_units = state['blue_units']
    else:
        blue_units = state['red_units']
    
    for unit in blue_units:
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            dest_pos = (unit[0] + dx, unit[1] + dy)
            if is_within_bounds(dest_pos) and dest_pos not in state[f'red_units' if state['current_player'] == 0 else 'blue_units']:
                legal_actions.append(f'move ({unit[0]}, {unit[1]}) to ({dest_pos[0]}, {dest_pos[1]})')
    
    if not legal_actions:
        legal_actions.append('pass')
    
    return legal_actions

# Get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    blue_units = state['blue_units']
    red_units = state['red_units']
    center_square_occupied = state['center_square_occupied']
    
    blue_obs = {
        'units': blue_units,
        'center_square_occupied': center_square_occupied,
        'turn_count': state['turn_count'],
        'current_player': state['current_player']
    }
    
    red_obs = {
        'units': red_units,
        'center_square_occupied': center_square_occupied,
        'turn_count': state['turn_count'],
        'current_player': state['current_player']
    }
    
    return [blue_obs, red_obs]