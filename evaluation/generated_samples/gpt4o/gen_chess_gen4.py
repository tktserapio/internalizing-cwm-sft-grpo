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

# Constants for the players
WHITE = 0
BLACK = 1

# Initial board setup
INITIAL_BOARD = [
    ["r", "n", "b", "q", "k"],
    ["p", "p", "p", "p", "p"],
    [".", ".", ".", ".", "."],
    ["P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K"]
]

# Helper function to create a deep copy of the board
def copy_board(board: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in board]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": copy_board(INITIAL_BOARD),
        "current_player": WHITE,
        "move_count": 0,
        "fifty_move_counter": 0,
        "last_pawn_or_capture": 0,
        "is_terminal": False,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        "board": copy_board(state["board"]),
        "current_player": 1 - state["current_player"],
        "move_count": state["move_count"] + 1,
        "fifty_move_counter": state["fifty_move_counter"],
        "last_pawn_or_capture": state["last_pawn_or_capture"],
        "is_terminal": state["is_terminal"],
        "winner": state["winner"]
    }

    # Parse the action
    parts = action.split('_')
    piece = parts[0]
    from_square = parts[1]
    to_square = parts[2]
    promotion = parts[3] if len(parts) == 4 else None

    from_rank = int(from_square[1]) - 1
    from_file = ord(from_square[0]) - ord('a')
    to_rank = int(to_square[1]) - 1
    to_file = ord(to_square[0]) - ord('a')

    # Move the piece
    new_state["board"][to_rank][to_file] = piece.upper() if state["current_player"] == WHITE else piece.lower()
    new_state["board"][from_rank][from_file] = '.'

    # Handle promotion
    if promotion:
        new_state["board"][to_rank][to_file] = promotion.upper() if state["current_player"] == WHITE else promotion.lower()

    # Update fifty-move rule counter
    if piece.upper() == 'P' or state["board"][to_rank][to_file] != '.':
        new_state["fifty_move_counter"] = 0
    else:
        new_state["fifty_move_counter"] += 1

    # Check for terminal state (checkmate, stalemate, etc.)
    if is_checkmate(new_state):
        new_state["is_terminal"] = True
        new_state["winner"] = state["current_player"]
    elif is_stalemate(new_state):
        new_state["is_terminal"] = True
        new_state["winner"] = None
    elif new_state["fifty_move_counter"] >= 50:
        new_state["is_terminal"] = True
        new_state["winner"] = None

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state["is_terminal"] else state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "White" if player_id == WHITE else "Black"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state["is_terminal"]:
        return [0.0, 0.0]
    if state["winner"] is None:
        return [0.5, 0.5]  # Draw
    return [1.0, 0.0] if state["winner"] == WHITE else [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["is_terminal"]:
        return []
    # Generate legal moves for the current player
    return generate_legal_moves(state)

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

# Helper functions for move generation and game state checks

def generate_legal_moves(state: State) -> List[Action]:
    """Generates all legal moves for the current player."""
    # Placeholder for move generation logic
    # You would implement the logic to generate all legal moves for the current player
    return []

def is_checkmate(state: State) -> bool:
    """Determines if the current player is in checkmate."""
    # Placeholder for checkmate detection logic
    return False

def is_stalemate(state: State) -> bool:
    """Determines if the current player is in stalemate."""
    # Placeholder for stalemate detection logic
    return False

# Note: The implementation of move generation, checkmate, and stalemate detection is non-trivial and requires a detailed understanding of chess rules and logic.