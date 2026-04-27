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
    source, target = action.split(' to ')
    sr, sc = map(int, source.split(','))
    tr, tc = map(int, target.split(','))
    
    # Check if the source and target positions are valid
    if not is_within_board((sr, sc)) or not is_within_board((tr, tc)):
        raise ValueError("Invalid move: positions out of bounds")
    
    # Update the unit's position
    if (sr, sc) in state['blue_units']:
        new_state['blue_units'].remove((sr, sc))
        new_state['blue_units'].append((tr, tc))
    elif (sr, sc) in state['red_units']:
        new_state['red_units'].remove((sr, sc))
        new_state['red_units'].append((tr, tc))
    
    # Check if the target position is adjacent to an opponent's unit
    for opp_pos in state['red_units'] + state['blue_units']:
        if abs(tr - opp_pos[0]) + abs(tc - opp_pos[1]) == 1:
            new_state['center_square_occupied'] = False
            new_state['turn_count'] += 1
            break
    else:
        new_state['center_square_occupied'] = False
    
    # Update the current player
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    # Check if the center square is occupied
    if new_state['center_square_occupied']:
        new_state['turn_count'] = 50
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
    if state['turn_count'] == 50:
        return [0.0, 0.0]
    elif state['center_square_occupied']:
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_moves = []
    for unit in state['blue_units']:
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nr, nc = unit[0] + dr, unit[1] + dc
            if is_within_board((nr, nc)) and (nr, nc) not in state['blue_units'] + state['red_units']:
                legal_moves.append(f'move ({unit[0]}, {unit[1]}) to ({nr}, {nc})')
    for unit in state['red_units']:
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nr, nc = unit[0] + dr, unit[1] + dc
            if is_within_board((nr, nc)) and (nr, nc) not in state['blue_units'] + state['red_units']:
                legal_moves.append(f'move ({unit[0]}, {unit[1]}) to ({nr}, {nc})')
    return legal_moves

# Get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    blue_obs = {'units': state['blue_units'], 'stunned_units': []}
    red_obs = {'units': state['red_units'], 'stunned_units': []}
    return [blue_obs, red_obs]