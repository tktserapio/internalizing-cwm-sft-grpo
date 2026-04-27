import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to check if a position is within the board boundaries
def is_within_board(row: int, col: int) -> bool:
    return 0 <= row <= 4 and 0 <= col <= 4

# Initial state setup
def get_initial_state() -> State:
    # Player 0 (Blue): Two units at (0, 0) and (0, 4)
    blue_units = [(0, 0), (0, 4)]
    # Player 1 (Red): Two units at (4, 0) and (4, 4)
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
    # Parse the action
    if action.startswith("move"):
        source, target = action.split()[1:]
        source = tuple(map(int, source[1:-1].split(',')))
        target = tuple(map(int, target[1:-1].split(',')))
        
        # Check if the move is valid
        if not is_within_board(*target):
            raise ValueError(f"Invalid target position: {target}")
        if target in state['blue_units'] or target in state['red_units']:
            raise ValueError(f"Target position is occupied: {target}")
        
        # Perform the move
        new_state['blue_units'].remove(source)
        new_state['blue_units'].append(target)
        new_state['red_units'].remove(target)
        new_state['red_units'].append(source)
        
        # Check if the center square is occupied
        if target == (2, 2):
            new_state['center_square_occupied'] = True
            return new_state
        
        # Update the current player
        new_state['current_player'] = 1 if new_state['current_player'] == 0 else 0
        new_state['turn_count'] += 1
        return new_state
    
    elif action == "pass":
        # Player passes their turn
        new_state['current_player'] = 1 if new_state['current_player'] == 0 else 0
        new_state['turn_count'] += 1
        return new_state
    
    else:
        raise ValueError(f"Unknown action: {action}")

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return "Blue" if player_id == 0 else "Red"

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state['center_square_occupied']:
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    current_player = state['current_player']
    
    if current_player == 0:
        units = state['blue_units']
    else:
        units = state['red_units']
    
    for unit in units:
        row, col = unit
        # Check horizontal movement
        if row > 0 and is_within_board(row - 1, col):
            legal_actions.append(f"move ({row},{col}) to ({row-1},{col})")
        if row < 4 and is_within_board(row + 1, col):
            legal_actions.append(f"move ({row},{col}) to ({row+1},{col})")
        if col > 0 and is_within_board(row, col - 1):
            legal_actions.append(f"move ({row},{col}) to ({row},{col-1})")
        if col < 4 and is_within_board(row, col + 1):
            legal_actions.append(f"move ({row},{col}) to ({row},{col+1})")
        if row > 0 and col > 0 and is_within_board(row - 1, col - 1):
            legal_actions.append(f"move ({row},{col}) to ({row-1},{col-1})")
        if row > 0 and col < 4 and is_within_board(row - 1, col + 1):
            legal_actions.append(f"move ({row},{col}) to ({row-1},{col+1})")
        if row < 4 and col > 0 and is_within_board(row + 1, col - 1):
            legal_actions.append(f"move ({row},{col}) to ({row+1},{col-1})")
        if row < 4 and col < 4 and is_within_board(row + 1, col + 1):
            legal_actions.append(f"move ({row},{col}) to ({row+1},{col+1})")
    
    if not legal_actions:
        legal_actions.append("pass")
    
    return legal_actions

# Get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    blue_units = state['blue_units']
    red_units = state['red_units']
    center_square_occupied = state['center_square_occupied']
    
    blue_observation = {
        'units': blue_units,
        'center_square_occupied': center_square_occupied,
        'turn_count': state['turn_count'],
        'current_player': state['current_player']
    }
    
    red_observation = {
        'units': red_units,
        'center_square_occupied': center_square_occupied,
        'turn_count': state['turn_count'],
        'current_player': state['current_player']
    }
    
    return [blue_observation, red_observation]