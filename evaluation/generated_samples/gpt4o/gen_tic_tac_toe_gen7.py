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
WINNING_LENGTH = 4
PLAYER_MARKS = ['x', 'o']

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        'current_player': 0,
        'winner': None,
        'is_draw': False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        'board': [row[:] for row in state['board']],  # Deep copy of the board
        'current_player': state['current_player'],
        'winner': state['winner'],
        'is_draw': state['is_draw']
    }
    
    row, col = map(int, action.split(','))
    current_mark = PLAYER_MARKS[state['current_player']]
    
    # Place the current player's mark on the board
    new_state['board'][row][col] = current_mark
    
    # Check for a win or draw
    if check_winner(new_state['board'], row, col, current_mark):
        new_state['winner'] = state['current_player']
    elif all(cell != '' for row in new_state['board'] for cell in row):
        new_state['is_draw'] = True
    
    # Switch player
    new_state['current_player'] = 1 - state['current_player']
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['winner'] is not None or state['is_draw']:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['winner'] is not None:
        return [1.0 if state['winner'] == i else -1.0 for i in range(2)]
    if state['is_draw']:
        return [0.5, 0.5]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['winner'] is not None or state['is_draw']:
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

def check_winner(board: List[List[str]], row: int, col: int, mark: str) -> bool:
    """Check if placing a mark at (row, col) results in a win."""
    def count_consecutive(r_delta: int, c_delta: int) -> int:
        count = 0
        r, c = row, col
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == mark:
            count += 1
            r += r_delta
            c += c_delta
        return count
    
    # Check all directions: horizontal, vertical, and two diagonals
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for r_delta, c_delta in directions:
        if count_consecutive(r_delta, c_delta) + count_consecutive(-r_delta, -c_delta) - 1 >= WINNING_LENGTH:
            return True
    return False