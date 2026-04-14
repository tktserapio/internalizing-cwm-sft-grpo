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

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    
    # Parse the action
    source_row, source_col, dest_row, dest_col = map(int, action.split(' to ')[1].split(','))
    
    # Check if the move is valid
    if not is_within_board(dest_row, dest_col):
        raise ValueError("Invalid destination")
    
    # Update the positions of the units
    if action.startswith('move'):
        if (source_row, source_col) in state['blue_units']:
            new_state['blue_units'].remove((source_row, source_col))
            new_state['blue_units'].append((dest_row, dest_col))
        elif (source_row, source_col) in state['red_units']:
            new_state['red_units'].remove((source_row, source_col))
            new_state['red_units'].append((dest_row, dest_col))
        else:
            raise ValueError("Source position not occupied by a unit")
        
        # Check for stun effect
        for unit in state['blue_units'] + state['red_units']:
            if abs(unit[0] - dest_row) + abs(unit[1] - dest_col) == 1:
                new_state['center_square_occupied'] = False
                break
        else:
            new_state['center_square_occupied'] = True
        
        new_state['turn_count'] += 1
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    
    raise ValueError("Unknown action")

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Blue' if player_id == 0 else 'Red'

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state['center_square_occupied']:
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    
    if state['current_player'] == 0:
        blue_units = state['blue_units']
    else:
        red_units = state['red_units']
    
    for unit in blue_units + red_units:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            dest_row, dest_col = unit[0] + dr, unit[1] + dc
            if is_within_board(dest_row, dest_col) and (dest_row, dest_col) not in blue_units + red_units:
                legal_actions.append(f'move {unit[0]}, {unit[1]} to {dest_row}, {dest_col}')
    
    if not legal_actions and state['turn_count'] >= 50:
        return ['pass']
    
    return legal_actions

# Get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    blue_units = state['blue_units']
    red_units = state['red_units']
    
    blue_obs = {'units': blue_units, 'stunned': []}
    red_obs = {'units': red_units, 'stunned': []}
    
    for unit in blue_units + red_units:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            dest_row, dest_col = unit[0] + dr, unit[1] + dc
            if is_within_board(dest_row, dest_col) and (dest_row, dest_col) not in blue_units + red_units:
                if (dest_row, dest_col) in blue_units:
                    blue_obs['stunned'].append((unit[0], unit[1]))
                elif (dest_row, dest_col) in red_units:
                    red_obs['stunned'].append((unit[0], unit[1]))
    
    return [blue_obs, red_obs]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print(initial_state)
    
    # Simulate a move
    state_after_move = apply_action(initial_state, 'move 0, 0 to 1, 1')
    print(state_after_move)
    
    # Get current player
    current_player = get_current_player(state_after_move)
    print(f"Current player: {get_player_name(current_player)}")
    
    # Get legal actions
    legal_actions = get_legal_actions(state_after_move)
    print(legal_actions)
    
    # Get observations
    observations = get_observations(state_after_move)
    print(observations)