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

# Helper function to check if a position is within the board bounds
def is_within_bounds(pos):
    return 0 <= pos[0] <= 4 and 0 <= pos[1] <= 4

# Initial state setup
def get_initial_state() -> State:
    # Player 0 (Blue) starts with units at (0, 0) and (0, 4)
    blue_units = [(0, 0), (0, 4)]
    # Player 1 (Red) starts with units at (4, 0) and (4, 4)
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
    old_pos, new_pos = parse_move(action)
    
    # Check if the move is valid
    if not is_within_bounds(new_pos):
        raise ValueError("Invalid move: Position out of bounds.")
    if not is_within_bounds(old_pos):
        raise ValueError("Invalid move: Old position out of bounds.")
    if new_pos in new_state['blue_units'] + new_state['red_units']:
        raise ValueError("Invalid move: Target position already occupied.")
    
    # Update the positions of the units
    if old_pos == new_pos:
        raise ValueError("Invalid move: Cannot move to the same position.")
    new_state['blue_units'].remove(old_pos)
    new_state['blue_units'].append(new_pos)
    new_state['red_units'].remove(old_pos)
    new_state['red_units'].append(new_pos)
    
    # Check for stun effect
    for unit in new_state['red_units']:
        if abs(unit[0] - new_pos[0]) + abs(unit[1] - new_pos[1]) == 1:
            new_state['red_units'].remove(unit)
            new_state['red_units'].append(unit)
            new_state['turn_count'] += 1
            break
    
    # Check if the center square is occupied
    if new_pos == (2, 2):
        new_state['center_square_occupied'] = True
        new_state['current_player'] = -4  # Terminal state
    
    new_state['turn_count'] += 1
    return new_state

# Parse the move string into positions
def parse_move(action: Action) -> tuple[tuple[int, int], tuple[int, int]]:
    parts = action.split(' to ')
    old_pos_str, new_pos_str = parts[0], parts[1]
    old_pos = tuple(map(int, old_pos_str.split(',')))
    new_pos = tuple(map(int, new_pos_str.split(',')))
    return old_pos, new_pos

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

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    for unit in state['blue_units']:
        for i in range(5):
            for j in range(5):
                if is_within_bounds((i, j)):
                    legal_actions.append(f"move {unit} to {(i, j)}")
    for unit in state['red_units']:
        for i in range(5):
            for j in range(5):
                if is_within_bounds((i, j)) and (i, j) != unit:
                    legal_actions.append(f"move {unit} to {(i, j)}")
    return legal_actions

# Get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    blue_obs = {'units': state['blue_units']}
    red_obs = {'units': state['red_units']}
    return [blue_obs, red_obs]