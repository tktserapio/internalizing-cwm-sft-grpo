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
def is_within_board(pos):
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
    src = tuple(map(int, src.split(',')))
    dest = tuple(map(int, dest.split(',')))
    
    # Check if the source and destination are valid positions
    if not is_within_board(src) or not is_within_board(dest):
        raise ValueError("Invalid move: Source or destination out of bounds.")
    
    # Check if the source position is occupied
    if src in new_state['blue_units'] or src in new_state['red_units']:
        raise ValueError("Invalid move: Source position occupied.")
    
    # Check if the destination position is occupied
    if dest in new_state['blue_units'] or dest in new_state['red_units']:
        raise ValueError("Invalid move: Destination position occupied.")
    
    # Move the unit
    if src in new_state['blue_units']:
        new_state['blue_units'].remove(src)
        new_state['blue_units'].append(dest)
    elif src in new_state['red_units']:
        new_state['red_units'].remove(src)
        new_state['red_units'].append(dest)
    
    # Update the current player
    new_state['current_player'] = 1 - new_state['current_player']
    new_state['turn_count'] += 1
    
    # Check if the center square is occupied
    if dest == (2, 2):
        new_state['center_square_occupied'] = True
    
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
    current_player_units = state['blue_units'] if state['current_player'] == 0 else state['red_units']
    for unit in current_player_units:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx != 0 or dy != 0:  # Diagonal move
                    dest = (unit[0] + dx, unit[1] + dy)
                    if is_within_board(dest) and dest not in state['blue_units'] and dest not in state['red_units']:
                        legal_actions.append(f'move {unit} to {dest}')
                else:  # Orthogonal move
                    for d in [dx, dy]:
                        dest = (unit[0] + d, unit[1])
                        if is_within_board(dest) and dest not in state['blue_units'] and dest not in state['red_units']:
                            legal_actions.append(f'move {unit} to {dest}')
    if not legal_actions:
        legal_actions.append('pass')
    return legal_actions

# Get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    blue_obs = {'units': state['blue_units'], 'stunned_units': []}
    red_obs = {'units': state['red_units'], 'stunned_units': []}
    return [blue_obs, red_obs]