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

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board_size": 4,  # Size of the board (4x4 triangular grid)
        "board": [[None for _ in range(i + 1)] for i in range(4)],  # 2D list representing the board
        "current_player": BLACK,  # Black starts first
        "winner": None  # No winner initially
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Parse the action
    row, col = map(int, action.split(','))
    
    # Create a deep copy of the state to avoid mutation
    new_state = {
        "board_size": state["board_size"],
        "board": [row[:] for row in state["board"]],
        "current_player": state["current_player"],
        "winner": state["winner"]
    }
    
    # Place the stone
    new_state["board"][row][col] = new_state["current_player"]
    
    # Check for a winner
    if check_winner(new_state, row, col):
        new_state["winner"] = new_state["current_player"]
    
    # Switch players
    new_state["current_player"] = WHITE if new_state["current_player"] == BLACK else BLACK
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state["winner"] is not None else state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == BLACK else "White"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["winner"] is None:
        return [0.0, 0.0]
    return [1.0, 0.0] if state["winner"] == BLACK else [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["winner"] is not None:
        return []
    
    legal_actions = []
    for row in range(state["board_size"]):
        for col in range(len(state["board"][row])):
            if state["board"][row][col] is None:
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{"board": state["board"], "current_player": state["current_player"]}] * 2

def check_winner(state: State, row: int, col: int) -> bool:
    """
    Check if the current player has won after placing a stone at (row, col).
    This function checks if the current player has connected all three sides.
    """
    # Placeholder for winner checking logic
    # Implement a graph traversal or union-find to check connectivity
    # This is a complex part of the implementation and requires careful design
    return False

# Note: The `check_winner` function needs to be implemented with a proper algorithm
# to check if the current player has connected all three sides of the board.