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
def is_within_board(row, col):
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
    new_state = copy.deepcopy(state)
    if action == 'pass':
        return new_state
    
    # Parse the action string
    source, target = action.split(' to ')
    sr, sc = map(int, source.split(','))
    tr, tc = map(int, target.split(','))
    
    # Check if the source and target positions are valid
    if not is_within_board(sr, sc) or not is_within_board(tr, tc):
        raise ValueError("Invalid move")
    
    # Update the source position
    for i, unit in enumerate(new_state['blue_units']):
        if unit == (sr, sc):
            new_state['blue_units'][i] = (tr, tc)
            break
    else:
        raise ValueError("Unit not found at source position")
    
    # Check if the target position is the center square
    if (tr, tc) == (2, 2):
        new_state['center_square_occupied'] = True
        return new_state
    
    # Check if the target position is adjacent to an opponent's unit
    for unit in new_state['red_units']:
        if abs(unit[0] - tr) + abs(unit[1] - tc) == 1:
            new_state['red_units'].append((tr, tc))
            new_state['red_units'].remove(unit)
            new_state['turn_count'] += 1
            return new_state
    
    # If no legal moves, pass the turn
    new_state['turn_count'] += 1
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return ['Blue', 'Red'][player_id]

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    if state['center_square_occupied']:
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    current_player = state['current_player']
    for unit in state['blue_units']:
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nr, nc = unit[0] + dr, unit[1] + dc
            if is_within_board(nr, nc):
                legal_actions.append(f'move ({unit[0]}, {unit[1]}) to ({nr}, {nc})')
    if len(legal_actions) == 0:
        return ['pass']
    return legal_actions

# Get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    blue_units = state['blue_units']
    red_units = state['red_units']
    return [
        {'units': blue_units},
        {'units': red_units}
    ]