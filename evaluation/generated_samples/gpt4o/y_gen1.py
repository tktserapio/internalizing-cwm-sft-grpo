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
BOARD_SIZE = 4  # Size of the board edge
NUM_CELLS = sum(range(1, BOARD_SIZE + 2))  # Total number of cells in a triangular board
PLAYER_NAMES = ["Black", "White"]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [None] * NUM_CELLS,  # None indicates an empty cell
        "current_player": 0,  # 0 for Black, 1 for White
        "winner": None  # None until a player wins
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        "board": state["board"][:],  # Copy the board
        "current_player": state["current_player"],
        "winner": state["winner"]
    }
    
    if new_state["winner"] is not None:
        return new_state  # No action if the game is already won

    # Parse the action
    row, col = map(int, action.split(','))
    cell_index = get_cell_index(row, col)

    # Place the stone
    if new_state["board"][cell_index] is None:
        new_state["board"][cell_index] = new_state["current_player"]
        # Check for a win condition
        if check_winner(new_state["board"], new_state["current_player"]):
            new_state["winner"] = new_state["current_player"]
        else:
            # Switch player
            new_state["current_player"] = 1 - new_state["current_player"]
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"] if state["winner"] is None else -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return PLAYER_NAMES[player_id]

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["winner"] is None:
        return [0.0, 0.0]
    elif state["winner"] == 0:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["winner"] is not None:
        return []

    return [
        f"{row},{col}"
        for row in range(BOARD_SIZE)
        for col in range(BOARD_SIZE)
        if state["board"][get_cell_index(row, col)] is None
    ]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{"board": state["board"], "current_player": state["current_player"]}] * 2

# Helper functions
def get_cell_index(row: int, col: int) -> int:
    """Convert a row, col pair to a linear index in the board array."""
    return sum(range(row + 1)) + col

def check_winner(board: List[int], player: int) -> bool:
    """Check if the given player has won."""
    # This function should implement a graph traversal to check for a connection
    # between all three sides. This is a complex task and requires a detailed
    # implementation of a pathfinding algorithm like DFS or BFS.
    # For simplicity, this function is a placeholder.
    return False

# Note: The `check_winner` function is a placeholder and needs a proper implementation
# to check for connections across the board. This typically involves graph traversal
# techniques like DFS or BFS to determine if a player's stones form a path touching
# all three sides of the board.