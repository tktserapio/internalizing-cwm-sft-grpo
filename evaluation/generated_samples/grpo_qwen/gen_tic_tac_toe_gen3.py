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

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [["." for _ in range(6)] for _ in range(6)],
        "current_player": 0,
        "winner": None,
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Convert action string to row, col
    row, col = map(int, action.split(","))
    
    # Check if the action is valid
    if state["board"][row][col] != ".":
        raise ValueError("Cell already occupied")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch current player
    state["current_player"] = 1 if state["current_player"] == 0 else 0
    
    # Check for win condition
    if check_win(state):
        state["winner"] = state["current_player"]
        state["game_over"] = True
    elif all("." not in row for row in state["board"]):
        state["winner"] = None
        state["game_over"] = True
    
    return state

def check_win(state: State) -> bool:
    """
    Checks if there is a winning line of four marks for the current player.
    Checks for horizontal, vertical, and diagonal lines.
    """
    board = state["board"]
    current_player = state["current_player"]
    
    # Check rows and columns
    for i in range(6):
        if all(board[i][j] == "x" if current_player == 0 else "o" for j in range(6)) or \
           all(board[j][i] == "x" if current_player == 0 else "o" for j in range(6)):
            return True
    
    # Check diagonals
    for i in range(3):  # Only need to check up to 3 because we're looking for 4 in a row
        if all(board[i + k][i + k] == "x" if current_player == 0 else "o" for k in range(4)) or \
           all(board[i + k][5 - i - k] == "x" if current_player == 0 else "o" for k in range(4)):
            return True
    
    return False

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["winner"] is None:
        return [0.0, 0.0]
    elif state["winner"] == 0:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    else:
        return [f"{row},{col}" for row in range(6) for col in range(6) if state["board"][row][col] == "."]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    board = state["board"]
    for i in range(6):
        for j in range(6):
            if board[i][j] == ".":
                board[i][j] = "x" if state["current_player"] == 0 else "o"
            else:
                board[i][j] = "."
        observations.append({
            "board": board.copy(),
            "current_player": state["current_player"],
            "winner": state["winner"],
            "game_over": state["game_over"]
        })
        board = state["board"].copy()
    return observations