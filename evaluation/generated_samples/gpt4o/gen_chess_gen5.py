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

# Constants for the board setup
INITIAL_BOARD = [
    ["r", "n", "b", "q", "k"],
    ["p", "p", "p", "p", "p"],
    [".", ".", ".", ".", "."],
    ["P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K"]
]

# Helper functions
def clone_board(board: List[List[str]]) -> List[List[str]]:
    """Creates a deep copy of the board."""
    return [row[:] for row in board]

def is_within_bounds(x: int, y: int) -> bool:
    """Checks if a position is within the board boundaries."""
    return 0 <= x < 5 and 0 <= y < 5

def get_piece_color(piece: str) -> int:
    """Returns 0 for white pieces, 1 for black pieces, and -1 for empty squares."""
    if piece.isupper():
        return 0  # White
    elif piece.islower():
        return 1  # Black
    else:
        return -1  # Empty

def position_to_algebraic(x: int, y: int) -> str:
    """Converts board coordinates to algebraic notation."""
    return f"{chr(ord('a') + y)}{5 - x}"

def algebraic_to_position(algebraic: str) -> (int, int):
    """Converts algebraic notation to board coordinates."""
    file, rank = algebraic
    return 5 - int(rank), ord(file) - ord('a')

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": clone_board(INITIAL_BOARD),
        "current_player": 0,
        "move_count": 0,
        "fifty_move_counter": 0,
        "is_terminal": False,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        "board": clone_board(state["board"]),
        "current_player": 1 - state["current_player"],
        "move_count": state["move_count"] + 1,
        "fifty_move_counter": state["fifty_move_counter"],
        "is_terminal": state["is_terminal"],
        "winner": state["winner"]
    }

    # Parse the action
    parts = action.split("_")
    piece, from_pos, to_pos = parts[0], parts[1], parts[2]
    from_x, from_y = algebraic_to_position(from_pos)
    to_x, to_y = algebraic_to_position(to_pos)

    # Move the piece
    new_state["board"][to_x][to_y] = new_state["board"][from_x][from_y]
    new_state["board"][from_x][from_y] = "."

    # Handle pawn promotion
    if len(parts) == 4:
        promotion_piece = parts[3]
        new_state["board"][to_x][to_y] = promotion_piece

    # Update fifty-move counter
    if piece.upper() == "P" or new_state["board"][to_x][to_y] != ".":
        new_state["fifty_move_counter"] = 0
    else:
        new_state["fifty_move_counter"] += 1

    # Check for terminal state (checkmate, stalemate, etc.)
    # This requires additional logic to determine if the game is over

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["is_terminal"]:
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "White" if player_id == 0 else "Black"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state["is_terminal"]:
        return [0.0, 0.0]
    if state["winner"] == 0:
        return [1.0, -1.0]
    elif state["winner"] == 1:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]  # Draw

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["is_terminal"]:
        return []

    legal_actions = []
    # Logic to generate legal actions for the current player
    # This involves iterating over the board, identifying pieces of the current player,
    # and generating valid moves for each piece based on chess rules.

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

# Note: The implementation of `get_legal_actions` and terminal state checks in `apply_action`
# are non-trivial and require detailed chess logic for move generation and game state evaluation.