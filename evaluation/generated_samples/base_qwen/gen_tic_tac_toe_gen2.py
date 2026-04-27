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

# Helper function to check if a player has won
def check_win(board: List[List[str]], player: str, win_length: int) -> bool:
    # Check horizontal lines
    for row in board:
        for i in range(len(row) - win_length + 1):
            if all(cell == player for cell in row[i:i+win_length]):
                return True
    
    # Check vertical lines
    for col in range(len(board[0])):
        for i in range(len(board) - win_length + 1):
            if all(board[i+row][col] == player for row in range(win_length)):
                return True
    
    # Check diagonal lines
    for offset in range(-win_length + 1, win_length):
        for i in range(len(board) - win_length + 1):
            if all(board[i+offset][i+j] == player for j in range(win_length)):
                return True
            if all(board[i+offset][i+j] == player for j in range(win_length-1, -1, -1)):
                return True
    
    return False

# Function to get the initial state
def get_initial_state() -> State:
    return {
        "board": [["." for _ in range(6)] for _ in range(6)],
        "current_player": 0,
        "winner": None,
        "is_draw": False
    }

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    row, col = map(int, action.split(","))
    if state["board"][row][col] != ".":
        raise ValueError("Cell already occupied")
    
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    state["current_player"] = (state["current_player"] + 1) % 2
    state["winner"] = None
    state["is_draw"] = all(all(cell != "." for cell in row) for row in state["board"])
    
    if state["is_draw"]:
        state["winner"] = "draw"
    elif check_win(state["board"], "x", 4):
        state["winner"] = "x"
    elif check_win(state["board"], "o", 4):
        state["winner"] = "o"
    
    return state

# Function to get the current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return "Player 1" if player_id == 0 else "Player 2"

# Function to get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state["winner"] == "draw":
        return [0.0, 0.0]
    elif state["winner"] == "x":
        return [1.0, 0.0]
    elif state["winner"] == "o":
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    for row in range(6):
        for col in range(6):
            if state["board"][row][col] == ".":
                legal_actions.append(f"{row},{col}")
    return legal_actions

# Function to get the observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    observations = [
        {"board": state["board"], "legal_actions": get_legal_actions(state)},
        {"board": state["board"], "legal_actions": get_legal_actions(state)}
    ]
    return observations