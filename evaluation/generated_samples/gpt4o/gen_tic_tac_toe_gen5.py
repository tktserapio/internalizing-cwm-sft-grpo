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
PLAYER_MARKS = ['x', 'o']

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        'current_player': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        'board': [row[:] for row in state['board']],
        'current_player': state['current_player'],
        'winner': state['winner']
    }
    
    if new_state['winner'] is not None:
        return new_state  # No more moves allowed if there's a winner

    row, col = map(int, action.split(','))
    current_mark = PLAYER_MARKS[new_state['current_player']]
    
    if new_state['board'][row][col] == '':
        new_state['board'][row][col] = current_mark
        if check_winner(new_state['board'], row, col, current_mark):
            new_state['winner'] = new_state['current_player']
        elif all(cell != '' for row in new_state['board'] for cell in row):
            new_state['winner'] = -1  # Draw
        else:
            new_state['current_player'] = 1 - new_state['current_player']
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player'] if state['winner'] is None else -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['winner'] is None:
        return [0.0, 0.0]
    elif state['winner'] == -1:
        return [0.5, 0.5]  # Draw
    else:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['winner'] is not None:
        return []
    
    actions = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if state['board'][row][col] == '':
                actions.append(f"{row},{col}")
    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{'board': state['board'], 'current_player': state['current_player']}] * 2

def check_winner(board: List[List[str]], row: int, col: int, mark: str) -> bool:
    """Check if placing a mark at (row, col) wins the game."""
    def check_direction(dx: int, dy: int) -> bool:
        count = 0
        for d in range(-WIN_LENGTH + 1, WIN_LENGTH):
            r, c = row + d * dx, col + d * dy
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == mark:
                count += 1
                if count == WIN_LENGTH:
                    return True
            else:
                count = 0
        return False
    
    # Check all directions: horizontal, vertical, and two diagonals
    return (check_direction(1, 0) or  # Horizontal
            check_direction(0, 1) or  # Vertical
            check_direction(1, 1) or  # Diagonal /
            check_direction(1, -1))   # Diagonal \