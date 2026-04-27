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
    dest_row, dest_col = map(int, action.split(' to ')[1].split(','))
    
    # Check if the source and destination are within the board bounds
    if not (0 <= src_row < 5 and 0 <= src_col < 5 and 0 <= dest_row < 5 and 0 <= dest_col < 5):
        return False
    
    # Check if the source and destination squares are empty
    if state.get(f'{src_row},{src_col}') == 'occupied':
        return False
    
    # Check if the destination square is already occupied
    if state.get(f'{dest_row},{dest_col}') == 'occupied':
        return False
    
    return True

def apply_action(state: State, action: Action) -> State:
    """Apply the given action to the state and return the new state."""
    new_state = copy.deepcopy(state)
    # Extract source and destination coordinates from the action string
    src_row, src_col = map(int, action.split(' to ')[0].split(','))
    dest_row, dest_col = map(int, action.split(' to ')[1].split(','))
    
    # Update the state with the new position of the unit
    new_state[f'{dest_row},{dest_col}'] = 'occupied'
    new_state.pop(f'{src_row},{src_col}')
    
    # Check if the destination square was adjacent to an opponent's unit
    if f'{dest_row},{dest_col}' in state and state[f'{dest_row},{dest_col}'] == 'opponent':
        new_state[f'{dest_row},{dest_col}'] = 'stunned'
    
    return new_state

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    initial_state = {
        '0,0': 'occupied',
        '0,4': 'occupied',
        '1,0': 'opponent',
        '1,4': 'opponent',
        '2,2': 'empty'
    }
    return initial_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    # Check if there are still units on the board
    if '0,0' in state or '0,4' in state or '1,0' in state or '1,4' in state:
        return 0 if '0,0' in state else 1
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    # In this simple implementation, we assume no running rewards until a winner is determined
    if get_current_player(state) != -4:
        return [0.0, 0.0]
    else:
        return [1.0, 0.0] if '2,2' in state['0,0'] else [0.0, 1.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for row in range(5):
        for col in range(5):
            if state.get(f'{row},{col}') == 'occupied':
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr != 0 or dc != 0:
                            dest_row, dest_col = row + dr, col + dc
                            if 0 <= dest_row < 5 and 0 <= dest_col < 5 and state.get(f'{dest_row},{dest_col}') == 'empty':
                                legal_actions.append(f'move ({row},{col}) to ({dest_row},{dest_col})')
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    # Since it's a perfect information game, each player sees the same state
    player_0_obs = {k: v for k, v in state.items() if k.startswith('0')}
    player_1_obs = {k: v for k, v in state.items() if k.startswith('1')}
    return [player_0_obs, player_1_obs]