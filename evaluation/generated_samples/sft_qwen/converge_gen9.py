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

# Helper functions
def is_valid_move(action: Action, state: State) -> bool:
    """Check if the given action is valid in the current state."""
    # Extract source and destination coordinates
    src, dst = action.split(' to ')
    src_row, src_col = map(int, src.split(','))
    dst_row, dst_col = map(int, dst.split(','))

    # Check if the source and destination are within the board bounds
    if not (0 <= src_row < 5 and 0 <= src_col < 5 and 0 <= dst_row < 5 and 0 <= dst_col < 5):
        return False

    # Check if the source and destination squares are empty
    if state.get(f'{src_row},{src_col}') != '0' and state.get(f'{dst_row},{dst_col}') != '0':
        return False

    # Check if the destination square is adjacent to an opponent's unit
    opponent_units = [unit for unit in state.values() if unit == '1']
    for opp_unit in opponent_units:
        opp_row, opp_col = map(int, opp_unit.split(','))
        if abs(src_row - opp_row) + abs(src_col - opp_col) == 1:
            return True

    return False

def apply_action(state: State, action: Action) -> State:
    """Apply the given action to the current state."""
    new_state = copy.deepcopy(state)
    # Extract source and destination coordinates
    src, dst = action.split(' to ')
    src_row, src_col = map(int, src.split(','))
    dst_row, dst_col = map(int, dst.split(','))

    # Update the source square to empty
    new_state[f'{src_row},{src_col}'] = '0'
    
    # Update the destination square with the source unit
    new_state[f'{dst_row},{dst_col}'] = f'{src_row},{src_col}'
    
    # Update the source square to empty
    new_state[f'{dst_row},{dst_col}'] = '1'

    return new_state

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    initial_state = {
        '0,0': '0',  # Player 0 unit at (0, 0)
        '0,4': '0',  # Player 0 unit at (0, 4)
        '1,0': '1',  # Player 1 unit at (4, 0)
        '1,4': '1',  # Player 1 unit at (4, 4)
        '2,2': '0',  # Center square (2, 2) initially empty
    }
    return initial_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    player_units = [unit for unit in state.values() if unit == '0']
    if len(player_units) > 0:
        return 0
    else:
        return 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return ['Blue', 'Red'][player_id]

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    # In this simple implementation, there are no rewards yet.
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    player_units = [unit for unit in state.values() if unit == '0']
    for unit in player_units:
        src_row, src_col = map(int, unit.split(','))
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, -1)]:
            dst_row, dst_col = src_row + dr, src_col + dc
            if 0 <= dst_row < 5 and 0 <= dst_col < 5 and state.get(f'{dst_row},{dst_col}') == '0':
                legal_actions.append(f'move {unit} to {dst_row},{dst_col}')
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {}
    player_1_obs = {}

    # Player 0 sees only its own units
    for key, value in state.items():
        if value == '0':
            player_0_obs[key] = value

    # Player 1 sees only its own units
    for key, value in state.items():
        if value == '1':
            player_1_obs[key] = value

    return [player_0_obs, player_1_obs]