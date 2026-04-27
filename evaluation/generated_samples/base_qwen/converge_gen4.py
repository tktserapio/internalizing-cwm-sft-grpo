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

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    if action == 'pass':
        return new_state
    
    # Parse the action string
    src, dest = action.split(' to ')
    src_row, src_col = map(int, src.split(','))
    dest_row, dest_col = map(int, dest.split(','))
    
    # Check if the source and destination positions are valid
    if not is_within_bounds((src_row, src_col)) or not is_within_bounds((dest_row, dest_col)):
        raise ValueError("Invalid move")
    
    # Get the unit being moved
    unit = None
    if state['current_player'] == 0:
        for u in state['blue_units']:
            if u == (src_row, src_col):
                unit = u
                break
    else:
        for u in state['red_units']:
            if u == (src_row, src_col):
                unit = u
                break
    
    if unit is None:
        raise ValueError("Unit not found")
    
    # Update the unit's position
    new_state['blue_units'] = state['blue_units'] if state['current_player'] == 0 else state['red_units']
    new_state['blue_units'].remove(unit)
    new_state['blue_units'].append((dest_row, dest_col))
    
    # Check for stun condition
    for other_unit in state['blue_units'] if state['current_player'] == 0 else state['red_units']:
        if abs(dest_row - other_unit[0]) + abs(dest_col - other_unit[1]) == 1:
            new_state['red_units'] = state['red_units'] if state['current_player'] == 0 else state['blue_units']
            new_state['red_units'].remove(other_unit)
            new_state['red_units'].append((other_unit[0], other_unit[1]))
            new_state['center_square_occupied'] = True
            return new_state
    
    # Increment turn count
    new_state['turn_count'] += 1
    new_state['current_player'] = 1 if state['current_player'] == 0 else 0
    
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
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    if state['current_player'] == 0:
        for unit in state['blue_units']:
            for dest in [(unit[0]+1, unit[1]), (unit[0]-1, unit[1]), (unit[0], unit[1]+1), (unit[0], unit[1]-1), (unit[0]+1, unit[1]+1), (unit[0]+1, unit[1]-1), (unit[0]-1, unit[1]+1), (unit[0]-1, unit[1]-1)]:
                if is_within_bounds(dest):
                    legal_actions.append(f'move ({unit[0]}, {unit[1]}) to ({dest[0]}, {dest[1]})')
    else:
        for unit in state['red_units']:
            for dest in [(unit[0]+1, unit[1]), (unit[0]-1, unit[1]), (unit[0], unit[1]+1), (unit[0], unit[1]-1), (unit[0]+1, unit[1]+1), (unit[0]+1, unit[1]-1), (unit[0]-1, unit[1]+1), (unit[0]-1, unit[1]-1)]:
                if is_within_bounds(dest):
                    legal_actions.append(f'move ({unit[0]}, {unit[1]}) to ({dest[0]}, {dest[1]})')
    
    if not legal_actions:
        return ['pass']
    return legal_actions

# Get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    blue_obs = {'units': state['blue_units']}
    red_obs = {'units': state['red_units']}
    return [blue_obs, red_obs]