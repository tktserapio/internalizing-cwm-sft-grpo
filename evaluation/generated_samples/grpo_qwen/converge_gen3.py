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

# Helper function to check if a given position is within the board boundaries
def is_within_bounds(pos: Tuple[int, int]) -> bool:
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
    new_state = state.copy()
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    
    # Parse the action string
    source_pos, dest_pos = action.split(' to ')[1], action.split(' to ')[2]
    source_pos = tuple(map(int, source_pos.split(',')))
    dest_pos = tuple(map(int, dest_pos.split(',')))
    
    # Check if the source and destination positions are valid
    if not is_within_bounds(source_pos) or not is_within_bounds(dest_pos):
        raise ValueError("Invalid position")
    
    # Move the unit
    if source_pos in state['blue_units']:
        new_state['blue_units'].remove(source_pos)
        new_state['blue_units'].append(dest_pos)
    elif source_pos in state['red_units']:
        new_state['red_units'].remove(source_pos)
        new_state['red_units'].append(dest_pos)
    
    # Update the current player
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    new_state['turn_count'] += 1
    
    # Check for stun effect
    for unit in state['blue_units']:
        if abs(unit[0] - dest_pos[0]) + abs(unit[1] - dest_pos[1]) == 1:
            new_state['blue_units'].remove(unit)
            break
    for unit in state['red_units']:
        if abs(unit[0] - dest_pos[0]) + abs(unit[1] - dest_pos[1]) == 1:
            new_state['red_units'].remove(unit)
            break
    
    # Check if the center square is occupied
    if dest_pos == (2, 2):
        new_state['center_square_occupied'] = True
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
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    for unit in state['blue_units']:
        for i in range(5):
            for j in range(5):
                if is_within_bounds((i, j)) and (i, j) != unit:
                    legal_actions.append(f'move {unit} to {(i, j)}')
    for unit in state['red_units']:
        for i in range(5):
            for j in range(5):
                if is_within_bounds((i, j)) and (i, j) != unit:
                    legal_actions.append(f'move {unit} to {(i, j)}')
    return legal_actions

# Get the observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    blue_obs = {'units': state['blue_units'], 'stunned_units': []}
    red_obs = {'units': state['red_units'], 'stunned_units': []}
    return [blue_obs, red_obs]