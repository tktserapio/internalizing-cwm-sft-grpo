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
def is_within_board(pos):
    return 0 <= pos[0] <= 4 and 0 <= pos[1] <= 4

# Initial state setup
def get_initial_state() -> State:
    # Initial positions for Player 0 (Blue)
    blue_units = [(0, 0), (0, 4)]
    # Initial positions for Player 1 (Red)
    red_units = [(4, 0), (4, 4)]
    # Game state dictionary
    state = {
        'blue_units': blue_units,
        'red_units': red_units,
        'current_player': 0,
        'turn_count': 0,
        'center_square_occupied': False
    }
    return state

# Apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    # Extract the source and destination coordinates from the action string
    src_pos, dst_pos = parse_action(action)
    
    # Check if the action is valid
    if not is_within_board(src_pos) or not is_within_board(dst_pos):
        raise ValueError("Invalid action: Source or destination out of bounds.")
    
    # Update the position of the unit
    if action.startswith('move'):
        new_state['blue_units'] = update_unit_position(new_state['blue_units'], src_pos, dst_pos) if new_state['current_player'] == 0 else update_unit_position(new_state['red_units'], src_pos, dst_pos)
    elif action == 'pass':
        new_state['current_player'] = 1 if new_state['current_player'] == 0 else 0
    
    # Increment the turn count
    new_state['turn_count'] += 1
    
    # Check if the center square is occupied
    if dst_pos == (2, 2):
        new_state['center_square_occupied'] = True
        new_state['current_player'] = -4  # Terminal state
    
    return new_state

# Parse the action string into source and destination positions
def parse_action(action: Action) -> tuple[tuple[int, int], tuple[int, int]]:
    parts = action.split(' to ')
    src_part, dst_part = parts[0], parts[1]
    src_pos = tuple(map(int, src_part[4:-1].split(',')))
    dst_pos = tuple(map(int, dst_part[3:-1].split(',')))
    return src_pos, dst_pos

# Update the position of a unit in the list of units
def update_unit_position(units, src_pos, dst_pos):
    index = units.index(src_pos)
    units[index] = dst_pos
    return units

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Player 0' if player_id == 0 else 'Player 1'

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    if state['center_square_occupied']:
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    current_player = state['current_player']
    units = state[f'red_units'] if current_player == 0 else state[f'blue_units']
    for unit in units:
        # Check possible moves for each unit
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            new_x, new_y = unit[0] + dx, unit[1] + dy
            if is_within_board((new_x, new_y)) and (new_x, new_y) not in units:
                legal_actions.append(f'move {unit} to ({new_x}, {new_y})')
    if not legal_actions and state['turn_count'] < 50:
        legal_actions.append('pass')
    return legal_actions

# Get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    blue_units = state['blue_units']
    red_units = state['red_units']
    return [{'units': blue_units}, {'units': red_units}]