import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
BOARD_SIZE = 6
WIN_LENGTH = 4
PLAYER_MARKS = ['x', 'o']

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        'current_player': 0,
        'is_terminal': False,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        'board': [row[:] for row in state['board']],  # Deep copy of the board
        'current_player': state['current_player'],
        'is_terminal': state['is_terminal'],
        'winner': state['winner']
    }
    
    row, col = map(int, action.split(','))
    player_mark = PLAYER_MARKS[state['current_player']]
    
    # Place the player's mark on the board
    new_state['board'][row][col] = player_mark
    
    # Check for a win condition
    if check_win(new_state['board'], row, col, player_mark):
        new_state['is_terminal'] = True
        new_state['winner'] = state['current_player']
    elif all(cell != '' for row in new_state['board'] for cell in row):
        # Check for a draw
        new_state['is_terminal'] = True
        new_state['winner'] = None
    
    # Switch to the next player
    new_state['current_player'] = 1 - state['current_player']
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state['is_terminal'] else state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['is_terminal']:
        if state['winner'] is not None:
            return [1.0, -1.0] if state['winner'] == 0 else [-1.0, 1.0]
        else:
            return [0.0, 0.0]  # Draw
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['is_terminal']:
        return []
    
    actions = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if state['board'][row][col] == '':
                actions.append(f"{row},{col}")
    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{'board': state['board'], 'current_player': state['current_player']} for _ in range(2)]

def check_win(board: List[List[str]], row: int, col: int, mark: str) -> bool:
    """Check if placing a mark at (row, col) results in a win."""
    return (check_line(board, row, col, mark, 1, 0) or  # Horizontal
            check_line(board, row, col, mark, 0, 1) or  # Vertical
            check_line(board, row, col, mark, 1, 1) or  # Diagonal \
            check_line(board, row, col, mark, 1, -1))   # Diagonal /

def check_line(board: List[List[str]], row: int, col: int, mark: str, dr: int, dc: int) -> bool:
    """Check a line in the board for a win condition."""
    count = 0
    for d in range(-WIN_LENGTH + 1, WIN_LENGTH):
        r, c = row + d * dr, col + d * dc
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == mark:
            count += 1
            if count == WIN_LENGTH:
                return True
        else:
            count = 0
    return False