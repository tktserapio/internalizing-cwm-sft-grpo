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
    else:
        # Parse the action string
        source, target = action.split(' to ')
        sr, sc = map(int, source.split(','))
        tr, tc = map(int, target.split(','))
        
        # Check if the move is valid
        if not is_within_board(tr, tc):
            raise ValueError("Target position is out of bounds.")
        if (tr, tc) in state['blue_units'] or (tr, tc) in state['red_units']:
            raise ValueError("Target position is occupied.")
        
        # Update the positions of the units
        new_state['blue_units'] = [(sr, sc) if (sr, sc) != (tr, tc) else (tr, tc) for sr, sc in state['blue_units']]
        new_state['red_units'] = [(sr, sc) if (sr, sc) != (tr, tc) else (tr, tc) for sr, sc in state['red_units']]
        
        # Check for stun condition
        for unit in state['blue_units']:
            if (unit[0], unit[1]) in [(tr, tc-1), (tr, tc+1), (tr-1, tc), (tr+1, tc)]:
                new_state['blue_units'] = [(sr, sc) if (sr, sc) != unit else (sr, sc) for sr, sc in state['blue_units']]
                break
        for unit in state['red_units']:
            if (unit[0], unit[1]) in [(tr, tc-1), (tr, tc+1), (tr-1, tc), (tr+1, tc)]:
                new_state['red_units'] = [(sr, sc) if (sr, sc) != unit else (sr, sc) for sr, sc in state['red_units']]
                break
        
        # Increment the turn count
        new_state['turn_count'] += 1
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        
        # Check if the center square is occupied
        if (2, 2) in state['blue_units']:
            new_state['center_square_occupied'] = True
            new_state['center_square_winner'] = 0
        elif (2, 2) in state['red_units']:
            new_state['center_square_occupied'] = True
            new_state['center_square_winner'] = 1
        
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
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    current_player = state['current_player']
    
    for unit in state[f'{current_player}_units']:
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nr, nc = unit[0] + dr, unit[1] + dc
            if is_within_board(nr, nc):
                legal_actions.append(f'move ({unit[0]}, {unit[1]}) to ({nr}, {nc})')
    
    if not legal_actions:
        return ['pass']
    return legal_actions

# Get the observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    blue_units = state['blue_units']
    red_units = state['red_units']
    center_square_occupied = state['center_square_occupied']
    center_square_winner = state['center_square_winner']
    
    blue_obs = {
        'units': blue_units,
        'units_stunned': [],
        'stunned_by': {},
        'center_square_occupied': center_square_occupied,
        'center_square_winner': center_square_winner
    }
    red_obs = {
        'units': red_units,
        'units_stunned': [],
        'stunned_by': {},
        'center_square_occupied': center_square_occupied,
        'center_square_winner': center_square_winner
    }
    
    return [blue_obs, red_obs]