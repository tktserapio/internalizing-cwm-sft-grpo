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

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [
            ['B', None, None, None, 'R'],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            ['R', None, None, None, 'B']
        ],
        'current_player': 0,
        'turn_count': 0,
        'stunned_units': []
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = new_state['current_player']
    board = new_state['board']
    turn_count = new_state['turn_count']
    
    # Parse the action
    src, dest = action.split(' to ')
    src_row, src_col = map(int, src.split(','))
    dest_row, dest_col = map(int, dest.split(','))

    # Check if the action is valid
    if not is_valid_move(board, src_row, src_col, dest_row, dest_col):
        raise ValueError("Invalid move")

    # Apply the move
    board[src_row][src_col], board[dest_row][dest_col] = board[dest_row][dest_col], board[src_row][src_col]

    # Update the current player
    new_state['current_player'] = 1 if player_id == 0 else 0

    # Update the turn count
    new_state['turn_count'] += 1

    # Handle stun mechanic
    handle_stun(board, src_row, src_col, dest_row, dest_col)

    return new_state

def is_valid_move(board: List[List[str]], src_row: int, src_col: int, dest_row: int, dest_col: int) -> bool:
    """
    Checks if the move is valid based on the game rules.
    """
    if board[dest_row][dest_col] is not None:
        return False
    if abs(src_row - dest_row) + abs(src_col - dest_col) != 1:
        return False
    return True

def handle_stun(board: List[List[str]], src_row: int, src_col: int, dest_row: int, dest_col: int):
    """
    Handles the stun mechanic.
    """
    if board[src_row][src_col] == 'R':
        opponent_id = 0
    else:
        opponent_id = 1
    
    if (src_row, src_col) in [(i, j) for i in range(5) for j in range(5) if abs(i - src_row) + abs(j - src_col) == 1]:
        board[dest_row][dest_col] = 'S'  # Stunned unit
        new_stunned_units = [unit for unit in board if unit == 'S']
        new_state = get_initial_state()
        new_state['stunned_units'] = new_stunned_units
        return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['current_player'] == -4:
        return [0.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    legal_actions = []

    for row in range(5):
        for col in range(5):
            if board[row][col] is not None:
                for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    dest_row, dest_col = row + dr, col + dc
                    if 0 <= dest_row < 5 and 0 <= dest_col < 5 and board[dest_row][dest_col] is None:
                        legal_actions.append(f'move ({row},{col}) to ({dest_row},{dest_col})')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    player_0_obs = {'board': board, 'current_player': state['current_player']}
    player_1_obs = {'board': board, 'current_player': state['current_player']}
    return [player_0_obs, player_1_obs]