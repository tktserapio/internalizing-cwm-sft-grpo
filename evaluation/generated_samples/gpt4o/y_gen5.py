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

# Constants for player identifiers
BLACK = 0
WHITE = 1

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board_size": 4,
        "board": [[None for _ in range(4)] for _ in range(4)],
        "current_player": BLACK,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        "board_size": state["board_size"],
        "board": [row[:] for row in state["board"]],
        "current_player": state["current_player"],
        "winner": state["winner"]
    }
    
    row, col = map(int, action.split(','))
    if new_state["board"][row][col] is not None:
        raise ValueError("Invalid action: Cell is already occupied.")
    
    new_state["board"][row][col] = new_state["current_player"]
    
    if check_winner(new_state["board"], new_state["current_player"]):
        new_state["winner"] = new_state["current_player"]
    
    new_state["current_player"] = WHITE if new_state["current_player"] == BLACK else BLACK
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state["winner"] is not None else state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == BLACK else "White"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. Non-zero values only at terminal states."""
    if state["winner"] is None:
        return [0.0, 0.0]
    return [1.0, 0.0] if state["winner"] == BLACK else [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["winner"] is not None:
        return []
    
    legal_actions = []
    for row in range(state["board_size"]):
        for col in range(state["board_size"]):
            if state["board"][row][col] is None:
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

def check_winner(board: List[List[int]], player: int) -> bool:
    """Check if the current player has won the game by connecting all three sides."""
    # This function should implement a pathfinding algorithm to check if a player has connected all three sides.
    # For simplicity, this function is a placeholder and should be implemented with a proper algorithm.
    return False

# Helper function to check connections and winning conditions
# This is a placeholder for the actual pathfinding algorithm needed to determine if a player has won.
def has_connection(board: List[List[int]], player: int) -> bool:
    # Implement a pathfinding algorithm like DFS or BFS to check for connections
    return False