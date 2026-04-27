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
PLAYER_BLACK = 0
PLAYER_WHITE = 1
BOARD_SIZE = 4  # Size of the board edge
TOTAL_CELLS = 10  # Total number of cells for a size-4 board

# Helper function to initialize an empty board
def create_empty_board(size: int) -> List[List[int]]:
    return [[-1 for _ in range(size)] for _ in range(size)]

# Required Functions

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": create_empty_board(BOARD_SIZE),
        "current_player": PLAYER_BLACK,
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
        "board": [row[:] for row in state["board"]],
        "current_player": state["current_player"],
        "winner": state["winner"]
    }
    
    # Place the stone on the board
    new_state["board"][row][col] = state["current_player"]
    
    # Check for a winner
    if check_winner(new_state["board"], state["current_player"]):
        new_state["winner"] = state["current_player"]
    
    # Switch players
    new_state["current_player"] = 1 - state["current_player"]
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state["winner"] is not None else state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == PLAYER_BLACK else "White"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["winner"] is None:
        return [0.0, 0.0]
    return [1.0, 0.0] if state["winner"] == PLAYER_BLACK else [0.0, 1.0]

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
    return [{"board": state["board"], "current_player": state["current_player"]}] * 2

# Helper function to check if the current player has won
def check_winner(board: List[List[int]], player: int) -> bool:
    # Implement a function to check if the player has connected all three sides
    # This is a complex function that requires graph traversal (e.g., DFS or BFS)
    # Placeholder for the actual implementation
    return False

# Note: The check_winner function needs to be implemented with a proper algorithm
# to determine if a player has connected all three sides of the board.