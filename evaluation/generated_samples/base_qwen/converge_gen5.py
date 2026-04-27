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
    """Check if the given action is valid based on the current state."""
    # Extract source and destination coordinates from the action string
    src_row, src_col = map(int, action.split(' to ')[0].split(','))
    dst_row, dst_col = map(int, action.split(' to ')[1].split(','))

    # Check if the source and destination are within the board boundaries
    if not (0 <= src_row < 5 and 0 <= src_col < 5 and 0 <= dst_row < 5 and 0 <= dst_col < 5):
        return False

    # Check if the source and destination squares are empty
    if state.get(f'{src_row},{src_col}') == 'occupied':
        return False
    if state.get(f'{dst_row},{dst_col}') == 'occupied':
        return False

    # Check if the move is orthogonal or diagonal
    if abs(src_row - dst_row) + abs(src_col - dst_col) != 1:
        return False

    return True

def apply_action(state: State, action: Action) -> State:
    """Apply the given action to the current state and return the new state."""
    new_state = copy.deepcopy(state)
    src_row, src_col = map(int, action.split(' to ')[0].split(','))
    dst_row, dst_col = map(int, action.split(' to ')[1].split(','))

    # Update the position of the moved unit
    new_state[f'{dst_row},{dst_col}'] = 'occupied'
    new_state.pop(f'{src_row},{src_col}')

    # Check for stun condition
    for key, value in new_state.items():
        if value == 'occupied' and (abs(int(key.split(',')[0]) - src_row) + abs(int(key.split(',')[1]) - src_col)) == 1:
            new_state[key] = 'stunned'

    return new_state

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    initial_state = {
        '0,0': 'occupied',
        '0,4': 'occupied',
        '4,0': 'occupied',
        '4,4': 'occupied',
        '2,2': 'empty'
    }
    return initial_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    # Check if the center square is occupied
    if state.get('2,2') == 'occupied':
        return -4  # Terminal state
    else:
        # Determine the current player based on the last action
        last_action = list(state.keys())[-1]
        if last_action.startswith('move (0,0'):
            return 0
        elif last_action.startswith('move (4,4'):
            return 1
        else:
            raise ValueError("Unexpected last action")

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return ['Blue', 'Red'][player_id]

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    # In this simple implementation, we assume there are no running rewards
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    if current_player == -4:
        return []  # Terminal state
    else:
        legal_actions = []
        for key, value in state.items():
            if value == 'occupied':
                for i in range(5):
                    for j in range(5):
                        if state.get(f'{i},{j}') == 'empty':
                            action = f'move ({key.split(",")[0]}, {key.split(",")[1]}) to ({i}, {j})'
                            if is_valid_move(action, state):
                                legal_actions.append(action)
        return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {}
    player_1_obs = {}

    for row in range(5):
        for col in range(5):
            if state.get(f'{row},{col}') == 'occupied':
                if state.get(f'{row},{col}') == 'occupied':
                    player_0_obs[(row, col)] = 1
                else:
                    player_1_obs[(row, col)] = 1

    return [player_0_obs, player_1_obs]