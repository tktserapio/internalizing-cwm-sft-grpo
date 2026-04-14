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

# Helper functions
def is_valid_move(action: Action, state: State) -> bool:
    """Check if the given action is valid based on the current state."""
    # Extract source and destination coordinates from the action string
    src_row, src_col = map(int, action.split(' to ')[0].split(','))
    dst_row, dst_col = map(int, action.split(' to ')[1].split(','))

    # Check if the source and destination are within the board bounds
    if not (0 <= src_row < 5 and 0 <= src_col < 5 and 0 <= dst_row < 5 and 0 <= dst_col < 5):
        return False

    # Check if the destination is empty
    if state.get(f'{dst_row},{dst_col}') is not None:
        return False

    # Check if the move is orthogonal or diagonal
    if abs(src_row - dst_row) > 1 or abs(src_col - dst_col) > 1:
        return False

    return True

def apply_action(state: State, action: Action) -> State:
    """Apply the given action to the state and return the new state."""
    new_state = state.copy()
    src_row, src_col = map(int, action.split(' to ')[0].split(','))
    dst_row, dst_col = map(int, action.split(' to ')[1].split(','))

    # Update the state with the new position of the unit
    new_state[f'{dst_row},{dst_col}'] = new_state.pop(f'{src_row},{src_col}')
    
    # Apply stun mechanic
    for key, value in new_state.items():
        if value == 'R' and (abs(int(key.split(',')[0]) - dst_row) <= 1 and abs(int(key.split(',')[1]) - dst_col) <= 1):
            new_state[key] = f'S{value}'
    
    return new_state

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    initial_state = {
        '0,0': 'B',  # Blue unit at (0,0)
        '0,4': 'B',  # Blue unit at (0,4)
        '4,0': 'R',  # Red unit at (4,0)
        '4,4': 'R'   # Red unit at (4,4)
    }
    return initial_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    blue_units = sum(1 for unit in state.values() if unit == 'B')
    red_units = sum(1 for unit in state.values() if unit == 'R')

    if blue_units > 0:
        return 0
    elif red_units > 0:
        return 1
    else:
        return -4  # Terminal state

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return ['Blue', 'Red'][player_id]

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    blue_units = sum(1 for unit in state.values() if unit == 'B')
    red_units = sum(1 for unit in state.values() if unit == 'R')

    if '2,2' in state:
        if state['2,2'] == 'B':
            return [1.0, 0.0]
        elif state['2,2'] == 'R':
            return [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for row in range(5):
        for col in range(5):
            if state.get(f'{row},{col}') == 'B':
                for dr, dc in [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 5 and 0 <= new_col < 5 and state.get(f'{new_row},{new_col}') is None:
                        legal_actions.append(f'move ({row},{col}) to ({new_row},{new_col})')
            elif state.get(f'{row},{col}') == 'R':
                for dr, dc in [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 5 and 0 <= new_col < 5 and state.get(f'{new_row},{new_col}') is None:
                        legal_actions.append(f'move ({row},{col}) to ({new_row},{new_col})')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {}
    player_1_obs = {}

    for row in range(5):
        for col in range(5):
            if state.get(f'{row},{col}') == 'B':
                player_0_obs[f'{row},{col}'] = state[f'{row},{col}']
            elif state.get(f'{row},{col}') == 'R':
                player_1_obs[f'{row},{col}'] = state[f'{row},{col}']

    return [player_0_obs, player_1_obs]