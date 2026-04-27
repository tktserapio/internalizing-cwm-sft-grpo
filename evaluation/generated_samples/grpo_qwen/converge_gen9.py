import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to check if a position is within bounds
def is_within_bounds(pos: tuple[int, int]) -> bool:
    return 0 <= pos[0] <= 4 and 0 <= pos[1] <= 4

# Initial state setup
def get_initial_state() -> State:
    return {
        'board': [
            [' ', ' ', ' ', ' ', ' '],
            [' ', 'B', ' ', 'B', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', 'R', ' '],
            [' ', ' ', ' ', ' ', ' ']
        ],
        'current_player': 0,
        'turn_count': 0,
        'center_square_occupied': False
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Parse the action
    source, target = action.split(' to ')
    source = tuple(map(int, source.split(',')))
    target = tuple(map(int, target.split(',')))

    # Check if the action is valid
    if not is_within_bounds(source) or not is_within_bounds(target):
        raise ValueError("Invalid action: positions out of bounds")
    
    board = state['board']
    current_player = state['current_player']
    turn_count = state['turn_count']

    # Get the source and target positions
    source_row, source_col = source
    target_row, target_col = target

    # Move the unit
    board[source_row][source_col] = ' '
    board[target_row][target_col] = 'B' if current_player == 0 else 'R'

    # Update the state
    state['board'] = board
    state['current_player'] = 1 if current_player == 0 else 0
    state['turn_count'] += 1

    # Check if the center square is occupied
    if target_row == 2 and target_col == 2:
        state['center_square_occupied'] = True

    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Blue' if player_id == 0 else 'Red'

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state['center_square_occupied']:
        return [1.0, 0.0] if get_current_player(state) == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    board = state['board']
    current_player = state['current_player']
    turn_count = state['turn_count']
    center_square_occupied = state['center_square_occupied']

    legal_actions = []

    # Player 0's turn
    if current_player == 0:
        for row in range(5):
            for col in range(5):
                if board[row][col] == 'B':
                    for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (-1, 0), (0, -1)]:
                        target_row, target_col = row + dr, col + dc
                        if is_within_bounds((target_row, target_col)) and board[target_row][target_col] == ' ':
                            legal_actions.append(f'move ({row},{col}) to ({target_row},{target_col})')
        if not legal_actions and turn_count < 50:
            legal_actions.append('pass')

    # Player 1's turn
    elif current_player == 1:
        for row in range(5):
            for col in range(5):
                if board[row][col] == 'R':
                    for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (-1, 0), (0, -1)]:
                        target_row, target_col = row + dr, col + dc
                        if is_within_bounds((target_row, target_col)) and board[target_row][target_col] == ' ':
                            legal_actions.append(f'move ({row},{col}) to ({target_row},{target_col})')
        if not legal_actions and turn_count < 50:
            legal_actions.append('pass')

    return legal_actions

# Get the observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    board = state['board']
    current_player = state['current_player']

    # Player 0's observation
    player_0_obs = {
        'board': board,
        'current_player': current_player,
        'turn_count': state['turn_count'],
        'center_square_occupied': state['center_square_occupied']
    }

    # Player 1's observation
    player_1_obs = {
        'board': board,
        'current_player': current_player,
        'turn_count': state['turn_count'],
        'center_square_occupied': state['center_square_occupied']
    }

    return [player_0_obs, player_1_obs]