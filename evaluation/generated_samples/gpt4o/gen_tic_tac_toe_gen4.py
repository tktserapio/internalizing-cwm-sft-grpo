import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
BOARD_SIZE = 6
WIN_LENGTH = 4
EMPTY_CELL = None
PLAYER_MARKS = ['x', 'o']

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [[EMPTY_CELL for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        'current_player': 0,
        'winner': None,
        'turn_count': 0
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = {
        'board': [row[:] for row in state['board']],  # Deep copy of the board
        'current_player': state['current_player'],
        'winner': state['winner'],
        'turn_count': state['turn_count'] + 1
    }
    
    row, col = map(int, action.split(','))
    current_mark = PLAYER_MARKS[state['current_player']]
    new_state['board'][row][col] = current_mark
    
    # Check for a winner
    if check_winner(new_state['board'], row, col, current_mark):
        new_state['winner'] = state['current_player']
    
    # Switch player
    new_state['current_player'] = 1 - state['current_player']
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['winner'] is not None or state['turn_count'] == BOARD_SIZE * BOARD_SIZE:
        return -4  # Terminal state
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['winner'] is not None:
        return [1.0 if state['winner'] == i else -1.0 for i in range(2)]
    if state['turn_count'] == BOARD_SIZE * BOARD_SIZE:
        return [0.0, 0.0]  # Draw
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['winner'] is not None or state['turn_count'] == BOARD_SIZE * BOARD_SIZE:
        return []  # No legal actions in terminal state
    return [
        f"{row},{col}"
        for row in range(BOARD_SIZE)
        for col in range(BOARD_SIZE)
        if state['board'][row][col] is EMPTY_CELL
    ]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

def check_winner(board: List[List[Any]], row: int, col: int, mark: str) -> bool:
    """Check if placing a mark at (row, col) results in a win."""
    def check_direction(delta_row: int, delta_col: int) -> bool:
        count = 0
        r, c = row, col
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == mark:
            count += 1
            r += delta_row
            c += delta_col
        return count >= WIN_LENGTH

    # Check all directions: horizontal, vertical, and two diagonals
    return (
        check_direction(0, 1) or  # Horizontal
        check_direction(1, 0) or  # Vertical
        check_direction(1, 1) or  # Diagonal /
        check_direction(1, -1)    # Diagonal \
    )