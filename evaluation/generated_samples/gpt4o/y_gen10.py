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
BOARD_SIZE = 4  # Size of the board's edge
NUM_CELLS = 10  # Total number of cells for a size-4 board

# Helper function to create an empty board
def create_empty_board(size: int) -> List[List[int]]:
    """Creates an empty board of given size."""
    return [[-1 for _ in range(size)] for _ in range(size)]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": create_empty_board(BOARD_SIZE),
        "current_player": 0,  # 0 for Black, 1 for White
        "turn_count": 0,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        "board": [row[:] for row in state["board"]],
        "current_player": state["current_player"],
        "turn_count": state["turn_count"] + 1,
        "winner": state["winner"]
    }
    
    row, col = map(int, action.split(','))
    new_state["board"][row][col] = state["current_player"]
    
    # Check if the current player has won
    if check_winner(new_state, row, col):
        new_state["winner"] = state["current_player"]
    
    # Switch player
    new_state["current_player"] = 1 - state["current_player"]
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["winner"] is not None:
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["winner"] is None:
        return [0.0, 0.0]
    return [1.0, 0.0] if state["winner"] == 0 else [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["winner"] is not None:
        return []
    
    legal_actions = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if state["board"][row][col] == -1:
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

def check_winner(state: State, row: int, col: int) -> bool:
    """Checks if the current player has won the game."""
    # This function needs to implement the logic to check if the current player
    # has connected all three sides of the board. This is a complex task and
    # requires a graph traversal algorithm to determine connectivity.
    # For simplicity, this is a placeholder.
    # Implementing the full connectivity check is non-trivial and requires
    # a depth-first search (DFS) or similar algorithm.
    return False

# Note: The check_winner function is a placeholder and needs to be implemented
# with a proper algorithm to check for connectivity across all three sides.