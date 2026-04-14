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

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board_size": 4,  # Size of the board (4x4 in this case)
        "board": [[None for _ in range(4)] for _ in range(4)],  # Empty board
        "current_player": 0,  # Black starts first, represented by 0
        "winner": None  # No winner initially
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        "board_size": state["board_size"],
        "board": [row[:] for row in state["board"]],  # Deep copy of the board
        "current_player": state["current_player"],
        "winner": state["winner"]
    }
    
    row, col = map(int, action.split(','))
    
    if new_state["board"][row][col] is not None:
        raise ValueError("Invalid action: Cell is already occupied.")
    
    # Place the stone for the current player
    new_state["board"][row][col] = new_state["current_player"]
    
    # Check for a win condition
    if check_winner(new_state, row, col):
        new_state["winner"] = new_state["current_player"]
    
    # Switch player
    new_state["current_player"] = 1 - new_state["current_player"]
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state["winner"] is not None else state["current_player"]

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
    
    actions = []
    for row in range(state["board_size"]):
        for col in range(state["board_size"]):
            if state["board"][row][col] is None:
                actions.append(f"{row},{col}")
    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{"board": state["board"], "current_player": state["current_player"]}] * 2

def check_winner(state: State, row: int, col: int) -> bool:
    """Check if the current player has won after placing a stone at (row, col)."""
    # This function should implement the logic to check if the current player has connected all three sides.
    # For simplicity, this is a placeholder and should be replaced with the actual winning logic.
    # Implementing a full connection check is complex and requires graph traversal algorithms.
    return False

# Note: The check_winner function is a placeholder and needs to be implemented with the actual logic to determine if a player has won.