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

# Helper function to check if a player has won
def has_won(board: List[List[str]], player: str) -> bool:
    # Check rows and columns
    for i in range(6):
        if all(board[i][j] == player for j in range(6)) or \
           all(board[j][i] == player for j in range(6)):
            return True
    # Check diagonals
    for i in range(3):  # Only need to check up to 3 because we need 4 in a row
        if all(board[i + k][i + k] == player for k in range(4)) or \
           all(board[i + k][5 - i - k] == player for k in range(4)):
            return True
    return False

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [["" for _ in range(6)] for _ in range(6)],
        "current_player": 0,
        "winner": None,
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    row, col = map(int, action.split(","))
    if state["board"][row][col] != "":
        raise ValueError("Cell already occupied")
    
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    state["current_player"] = (state["current_player"] + 1) % 2
    
    if has_won(state["board"], "x"):
        state["winner"] = "x"
        state["game_over"] = True
    elif has_won(state["board"], "o"):
        state["winner"] = "o"
        state["game_over"] = True
    elif all(state["board"][i][j] != "" for i in range(6) for j in range(6)):
        state["winner"] = "draw"
        state["game_over"] = True
    
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["winner"] == "x":
        return [1.0, 0.0]
    elif state["winner"] == "o":
        return [0.0, 1.0]
    elif state["winner"] == "draw":
        return [0.5, 0.5]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    return [f"{i},{j}" for i in range(6) for j in range(6) if state["board"][i][j] == ""]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    for i in range(6):
        for j in range(6):
            if state["board"][i][j] == "":
                observations.append({
                    "board": state["board"],
                    "current_player": state["current_player"],
                    "winner": state["winner"],
                    "game_over": state["game_over"]
                })
            else:
                observations.append({
                    "board": state["board"],
                    "current_player": state["current_player"],
                    "winner": state["winner"],
                    "game_over": state["game_over"],
                    "action_taken": f"{i},{j}"
                })
    return observations