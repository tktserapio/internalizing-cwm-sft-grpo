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

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [['' for _ in range(6)] for _ in range(6)],  # 6x6 board initialized to empty strings
        "current_player": 0,  # Player 0 starts
        "is_terminal": False,  # Game is not over initially
        "winner": None  # No winner initially
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        "board": [row[:] for row in state["board"]],  # Deep copy of the board
        "current_player": state["current_player"],
        "is_terminal": state["is_terminal"],
        "winner": state["winner"]
    }
    
    row, col = map(int, action.split(','))
    current_player_mark = 'x' if state["current_player"] == 0 else 'o'
    
    # Place the current player's mark on the board
    new_state["board"][row][col] = current_player_mark
    
    # Check for a win condition
    if check_win(new_state["board"], row, col, current_player_mark):
        new_state["is_terminal"] = True
        new_state["winner"] = state["current_player"]
    elif all(cell != '' for row in new_state["board"] for cell in row):
        # Check for a draw condition
        new_state["is_terminal"] = True
        new_state["winner"] = None
    
    # Switch to the other player
    new_state["current_player"] = 1 - state["current_player"]
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state["is_terminal"] else state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Player X' if player_id == 0 else 'Player O'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state["is_terminal"]:
        return [0.0, 0.0]
    if state["winner"] is None:
        return [0.5, 0.5]  # Draw
    return [1.0, 0.0] if state["winner"] == 0 else [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["is_terminal"]:
        return []
    return [f"{r},{c}" for r in range(6) for c in range(6) if state["board"][r][c] == '']

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

def check_win(board: List[List[str]], row: int, col: int, mark: str) -> bool:
    """Check if placing a mark at (row, col) results in a win."""
    return (
        check_line(board, row, col, mark, 1, 0) or  # Horizontal
        check_line(board, row, col, mark, 0, 1) or  # Vertical
        check_line(board, row, col, mark, 1, 1) or  # Diagonal \
        check_line(board, row, col, mark, 1, -1)    # Diagonal /
    )

def check_line(board: List[List[str]], row: int, col: int, mark: str, dr: int, dc: int) -> bool:
    """Check a line in the board for a winning condition."""
    count = 0
    # Check in the positive direction
    r, c = row, col
    while 0 <= r < 6 and 0 <= c < 6 and board[r][c] == mark:
        count += 1
        r += dr
        c += dc
    
    # Check in the negative direction
    r, c = row - dr, col - dc
    while 0 <= r < 6 and 0 <= c < 6 and board[r][c] == mark:
        count += 1
        r -= dr
        c -= dc
    
    return count >= 4