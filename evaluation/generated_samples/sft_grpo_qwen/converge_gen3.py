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

# Helper function to parse coordinates
def parse_coordinates(coord_str: str) -> Tuple[int, int]:
    row, col = map(int, coord_str.strip('()').split(','))
    return row, col

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

# Apply action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    else:
        old_row, old_col = parse_coordinates(action.split()[1])
        new_row, new_col = parse_coordinates(action.split()[3])
        new_state['blue_units'] = [
            (old_row, old_col) if (old_row, old_col) in new_state['blue_units'] else (new_row, new_col)
        ]
        new_state['red_units'] = [
            (old_row, old_col) if (old_row, old_col) in new_state['red_units'] else (new_row, new_col)
        ]
        new_state['turn_count'] += 1
        return new_state

# Get current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get player name
def get_player_name(player_id: int) -> str:
    return 'Blue' if player_id == 0 else 'Red'

# Get rewards
def get_rewards(state: State) -> List[float]:
    if state['center_square_occupied']:
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    current_player = state['current_player']
    for unit in state[f'{current_player}_units']:
        row, col = unit
        # Check horizontal, vertical, and diagonal moves
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 5 and 0 <= new_col < 5 and (new_row, new_col) not in state[f'{current_player}_units']:
                legal_actions.append(f'move ({row},{col}) to ({new_row},{new_col})')
    if not legal_actions:
        legal_actions.append('pass')
    return legal_actions

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    blue_units = state['blue_units']
    red_units = state['red_units']
    center_square_occupied = (2, 2) in blue_units or (2, 2) in red_units
    return [
        {
            'units': blue_units,
            'center_square_occupied': center_square_occupied
        },
        {
            'units': red_units,
            'center_square_occupied': center_square_occupied
        }
    ]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    print("Legal Actions:", get_legal_actions(initial_state))