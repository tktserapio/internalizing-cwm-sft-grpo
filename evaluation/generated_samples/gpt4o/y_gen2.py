import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Dict, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants for player identification
BLACK = 0
WHITE = 1

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board_size": 4,  # Change this for different board sizes
        "board": [[None for _ in range(row + 1)] for row in range(4)],
        "current_player": BLACK,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Parse the action
    row, col = map(int, action.split(','))
    
    # Create a new state to avoid mutating the original
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
    new_state["current_player"] = WHITE if state["current_player"] == BLACK else BLACK
    
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
        for col in range(row + 1):
            if state["board"][row][col] is None:
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{"board": state["board"], "current_player": state["current_player"]}] * 2

def check_winner(state: State, last_row: int, last_col: int) -> bool:
    """Check if the current player has won the game."""
    # Implement a connection check algorithm to determine if the current player has connected all three sides.
    # This is a complex task and requires graph traversal algorithms like DFS or BFS.
    # For simplicity, this function is a placeholder and should be implemented with a proper algorithm.
    return False

# Note: The check_winner function is a placeholder and needs a proper implementation to check for winning conditions.