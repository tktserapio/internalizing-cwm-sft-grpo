import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple
import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
BOARD_SIZE = 4  # Size of the board edge
NUM_CELLS = 10  # Total number of cells for a size-4 board
PLAYER_NAMES = ["Black", "White"]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [None] * NUM_CELLS,  # None indicates an empty cell
        "current_player": 0,  # 0 for Black, 1 for White
        "winner": None  # None indicates no winner yet
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    row, col = map(int, action.split(','))
    cell_index = get_cell_index(row, col)
    
    if new_state["board"][cell_index] is not None:
        raise ValueError("Cell is already occupied")
    
    new_state["board"][cell_index] = new_state["current_player"]
    
    if check_winner(new_state, new_state["current_player"]):
        new_state["winner"] = new_state["current_player"]
    
    new_state["current_player"] = 1 - new_state["current_player"]
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["winner"] is not None:
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return PLAYER_NAMES[player_id]

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["winner"] is None:
        return [0.0, 0.0]
    return [1.0 if state["winner"] == i else 0.0 for i in range(2)]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["winner"] is not None:
        return []
    
    legal_actions = []
    for index, cell in enumerate(state["board"]):
        if cell is None:
            row, col = get_row_col(index)
            legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

def get_cell_index(row: int, col: int) -> int:
    """Converts row, col to a linear cell index."""
    return row * (row + 1) // 2 + col

def get_row_col(index: int) -> Tuple[int, int]:
    """Converts a linear cell index to row, col."""
    row = 0
    while index >= (row + 1) * (row + 2) // 2:
        row += 1
    col = index - row * (row + 1) // 2
    return row, col

def check_winner(state: State, player: int) -> bool:
    """Checks if the given player has won the game."""
    # This function should implement a graph traversal to check if the player
    # has connected all three sides. This is a complex function that requires
    # a depth-first search (DFS) or breadth-first search (BFS) on the hex grid.
    # For simplicity, this is a placeholder.
    # Implement the actual connection-checking logic here.
    return False

# Note: The check_winner function is a placeholder and needs to be implemented
# with a proper algorithm to check for connected paths touching all three sides.