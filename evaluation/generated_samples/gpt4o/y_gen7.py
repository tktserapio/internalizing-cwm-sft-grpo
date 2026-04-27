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

# Constants for players
BLACK = 0
WHITE = 1
EMPTY = -1

# Function to initialize the game state
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initialize a size-4 board with all cells empty
    board_size = 4
    total_cells = sum(range(1, board_size + 2))  # 10 cells for size-4
    board = [EMPTY] * total_cells
    return {
        "board": board,
        "current_player": BLACK,
        "board_size": board_size,
        "winner": None
    }

# Function to apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    new_state["board"] = state["board"][:]
    
    # Parse the action
    row, col = map(int, action.split(','))
    cell_index = get_cell_index(row, col, state["board_size"])
    
    # Place the stone for the current player
    new_state["board"][cell_index] = state["current_player"]
    
    # Check for a winner
    if check_winner(new_state, cell_index):
        new_state["winner"] = state["current_player"]
    
    # Switch player
    new_state["current_player"] = WHITE if state["current_player"] == BLACK else BLACK
    
    return new_state

# Function to get the current player
def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["winner"] is not None:
        return -4
    return state["current_player"]

# Function to get the player name
def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == BLACK else "White"

# Function to get rewards
def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["winner"] is None:
        return [0.0, 0.0]
    return [1.0, 0.0] if state["winner"] == BLACK else [0.0, 1.0]

# Function to get legal actions
def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["winner"] is not None:
        return []
    return [f"{row},{col}" for row in range(state["board_size"]) for col in range(row + 1)
            if state["board"][get_cell_index(row, col, state["board_size"])] == EMPTY]

# Function to get observations
def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{"board": state["board"], "current_player": state["current_player"]}] * 2

# Helper function to get the linear index of a cell in the board
def get_cell_index(row: int, col: int, board_size: int) -> int:
    """Converts a (row, col) pair to a linear index in the board array."""
    return sum(range(row + 1)) + col

# Placeholder for winner checking logic
def check_winner(state: State, last_move_index: int) -> bool:
    """Checks if the current player has won after placing a stone at last_move_index."""
    # Implement the logic to check if the current player has a winning connection
    # This requires checking if there is a path connecting all three sides
    return False

# Note: The `check_winner` function needs to be implemented with logic to determine
# if a player has formed a connected path touching all three sides of the board.