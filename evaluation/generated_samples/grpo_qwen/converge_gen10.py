import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to check if a given position is within the board boundaries
def is_within_board(row: int, col: int) -> bool:
    return 0 <= row <= 4 and 0 <= col <= 4

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
    new_state = state.copy()
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    else:
        # Parse the action string
        src_row, src_col, dest_row, dest_col = map(int, action.split(' to ')[1].split(','))
        
        # Check if the source and destination are valid
        if not is_within_board(src_row, src_col) or not is_within_board(dest_row, dest_col):
            raise ValueError("Invalid move: source or destination out of bounds")
        
        # Check if the source and destination are adjacent
        if abs(src_row - dest_row) > 1 or abs(src_col - dest_col) > 1:
            raise ValueError("Invalid move: source and destination are not adjacent")
        
        # Check if the destination is already occupied
        if (dest_row, dest_col) in state['blue_units'] or (dest_row, dest_col) in state['red_units']:
            raise ValueError("Invalid move: destination is occupied")
        
        # Perform the move
        if (src_row, src_col) in state['blue_units']:
            new_state['blue_units'].remove((src_row, src_col))
            new_state['blue_units'].append((dest_row, dest_col))
        elif (src_row, src_col) in state['red_units']:
            new_state['red_units'].remove((src_row, src_col))
            new_state['red_units'].append((dest_row, dest_col))
        
        # Update the current player
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        
        # Check if the center square is occupied
        if (2, 2) in new_state['blue_units']:
            new_state['center_square_occupied'] = True
            new_state['center_square_winner'] = 0
        elif (2, 2) in new_state['red_units']:
            new_state['center_square_occupied'] = True
            new_state['center_square_winner'] = 1
        
        new_state['turn_count'] += 1
        return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Blue' if player_id == 0 else 'Red'

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state['center_square_occupied']:
        if state['center_square_winner'] == 0:
            return [1.0, 0.0]
        else:
            return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    if state['current_player'] == 0:
        for unit in state['blue_units']:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i != 0 or j != 0:  # Avoid moving to the same position
                        dest_row, dest_col = unit[0] + i, unit[1] + j
                        if is_within_board(dest_row, dest_col) and (dest_row, dest_col) not in state['blue_units'] and (dest_row, dest_col) not in state['red_units']:
                            legal_actions.append(f'move ({unit[0]}, {unit[1]}) to ({dest_row}, {dest_col})')
    else:
        for unit in state['red_units']:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i != 0 or j != 0:  # Avoid moving to the same position
                        dest_row, dest_col = unit[0] + i, unit[1] + j
                        if is_within_board(dest_row, dest_col) and (dest_row, dest_col) not in state['blue_units'] and (dest_row, dest_col) not in state['red_units']:
                            legal_actions.append(f'move ({unit[0]}, {unit[1]}) to ({dest_row}, {dest_col})')
    if not legal_actions:
        legal_actions.append('pass')
    return legal_actions

# Get the observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    blue_units = state['blue_units']
    red_units = state['red_units']
    blue_obs = {'units': blue_units, 'center_square_occupied': state['center_square_occupied'], 'center_square_winner': state['center_square_winner']}
    red_obs = {'units': red_units, 'center_square_occupied': state['center_square_occupied'], 'center_square_winner': state['center_square_winner']}
    return [blue_obs, red_obs]