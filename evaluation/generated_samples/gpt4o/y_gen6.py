import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants for player identification
BLACK = 0
WHITE = 1
NO_PLAYER = -1

# Helper function to convert action string to board coordinates
def action_to_coords(action: Action) -> Tuple[int, int]:
    row, col = map(int, action.split(','))
    return row, col

# Helper function to convert board coordinates to action string
def coords_to_action(row: int, col: int) -> Action:
    return f"{row},{col}"

# Initialize the game state
def get_initial_state() -> State:
    return {
        "board_size": 4,  # Size of the board (4x4 for a size-4 board)
        "board": [[NO_PLAYER for _ in range(4)] for _ in range(4)],  # Empty board
        "current_player": BLACK,  # Black starts first
        "winner": None  # No winner initially
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = {
        "board_size": state["board_size"],
        "board": [row[:] for row in state["board"]],  # Deep copy of the board
        "current_player": state["current_player"],
        "winner": state["winner"]
    }
    
    row, col = action_to_coords(action)
    if new_state["board"][row][col] == NO_PLAYER:
        new_state["board"][row][col] = state["current_player"]
        if check_winner(new_state, row, col):
            new_state["winner"] = state["current_player"]
        else:
            new_state["current_player"] = WHITE if state["current_player"] == BLACK else BLACK
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state["current_player"] if state["winner"] is None else -4

# Get the player name
def get_player_name(player_id: int) -> str:
    return "Black" if player_id == BLACK else "White"

# Get rewards for the players
def get_rewards(state: State) -> List[float]:
    if state["winner"] is None:
        return [0.0, 0.0]
    return [1.0, 0.0] if state["winner"] == BLACK else [0.0, 1.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state["winner"] is not None:
        return []
    return [coords_to_action(row, col) for row in range(state["board_size"]) for col in range(state["board_size"]) if state["board"][row][col] == NO_PLAYER]

# Get observations for both players
def get_observations(state: State) -> List[PlayerObservation]:
    return [{"board": state["board"], "current_player": state["current_player"]}] * 2

# Check if the current player has won after placing a stone at (row, col)
def check_winner(state: State, row: int, col: int) -> bool:
    # This function should implement the logic to check if the current player has connected all three sides
    # For simplicity, this is a placeholder and should be replaced with the actual logic
    return False

# Note: The check_winner function is a placeholder and needs to be implemented with the actual logic
# to determine if a player has won the game by connecting all three sides.