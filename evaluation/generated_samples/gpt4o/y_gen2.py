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

# Constants for player identification
BLACK = 0
WHITE = 1
EMPTY = -1
TERMINAL_STATE = -4

# Helper function to create an empty board
def create_empty_board(size: int) -> List[List[int]]:
    return [[EMPTY for _ in range(size)] for _ in range(size)]

# Function to get the initial state of the game
def get_initial_state() -> State:
    return {
        "board": create_empty_board(4),  # Size-4 board
        "current_player": BLACK,
        "winner": None
    }

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    row, col = map(int, action.split(','))
    new_state = {
        "board": [row[:] for row in state["board"]],  # Deep copy of the board
        "current_player": WHITE if state["current_player"] == BLACK else BLACK,
        "winner": state["winner"]
    }
    new_state["board"][row][col] = state["current_player"]
    if check_winner(new_state, row, col):
        new_state["winner"] = state["current_player"]
    return new_state

# Function to get the current player
def get_current_player(state: State) -> int:
    return TERMINAL_STATE if state["winner"] is not None else state["current_player"]

# Function to get the player name
def get_player_name(player_id: int) -> str:
    return "Black" if player_id == BLACK else "White"

# Function to get rewards
def get_rewards(state: State) -> List[float]:
    if state["winner"] is None:
        return [0.0, 0.0]
    return [1.0, 0.0] if state["winner"] == BLACK else [0.0, 1.0]

# Function to get legal actions
def get_legal_actions(state: State) -> List[Action]:
    if state["winner"] is not None:
        return []
    size = len(state["board"])
    return [f"{r},{c}" for r in range(size) for c in range(size) if state["board"][r][c] == EMPTY]

# Function to get observations
def get_observations(state: State) -> List[PlayerObservation]:
    return [state, state]  # Perfect information game

# Helper function to check if a player has won
def check_winner(state: State, row: int, col: int) -> bool:
    # Implement a function to check if the current player has won
    # This is a complex function that involves checking if the placed stone connects all three sides
    # For simplicity, we will assume this function is implemented correctly
    # Placeholder for the actual connection-checking logic
    return False

# Note: The check_winner function is a placeholder and needs to be implemented with the logic
# to determine if a player has connected all three sides of the board.