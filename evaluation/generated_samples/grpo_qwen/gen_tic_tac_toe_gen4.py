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
        "turn_count": 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Convert action to row, col
    row, col = map(int, action.split(","))
    
    # Check if the action is valid
    if state["board"][row][col] != ".":
        raise ValueError("Cell is already occupied.")
    
    # Apply the action
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    state["turn_count"] += 1
    
    # Determine the winner
    winner = determine_winner(state)
    if winner:
        return {"board": state["board"], "current_player": None, "winner": winner, "turn_count": state["turn_count"]}
    
    # Switch player
    state["current_player"] = 1 if state["current_player"] == 0 else 0
    
    return state

def determine_winner(state: State) -> int:
    """
    Determines if there is a winner based on the current state of the board.
    Checks for horizontal, vertical, and diagonal lines of four marks.
    """
    board = state["board"]
    n = len(board)
    
    # Check rows and columns
    for i in range(n):
        if all(board[i][j] == "x" for j in range(n)) or all(board[i][j] == "o" for j in range(n)):
            return 0 if board[i][0] == "x" else 1
        if all(board[j][i] == "x" for j in range(n)) or all(board[j][i] == "o" for j in range(n)):
            return 0 if board[0][i] == "x" else 1
    
    # Check diagonals
    for i in range(n):
        if all(board[i][i] == "x" for i in range(n)) or all(board[i][n-1-i] == "x" for i in range(n)):
            return 0 if board[0][0] == "x" else 1
        if all(board[i][i] == "o" for i in range(n)) or all(board[i][n-1-i] == "o" for i in range(n)):
            return 0 if board[0][0] == "o" else 1
    
    # Check if all cells are filled
    if state["turn_count"] == n * n:
        return None
    
    return None

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 1" if player_id == 0 else "Player 2"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["winner"] is not None:
        return [1.0, 0.0] if state["winner"] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["winner"] is not None:
        return []
    return ["{},{}".format(row, col) for row in range(6) for col in range(6) if state["board"][row][col] == "."]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    board = state["board"]
    for row in range(6):
        for col in range(6):
            if board[row][col] == ".":
                board[row][col] = "x" if state["current_player"] == 0 else "o"
                observations.append({
                    "board": board.copy(),
                    "current_player": 1 - state["current_player"],
                    "turn_count": state["turn_count"]
                })
                board[row][col] = "."
    return observations