import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
INITIAL_BOARD = [
    ['r', 'n', 'b', 'q', 'k'],
    ['p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K']
]

PLAYER_NAMES = ["White", "Black"]

# Helper function to create a deep copy of the board
def copy_board(board: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in board]

# Function to get the initial state of the game
def get_initial_state() -> State:
    return {
        "board": copy_board(INITIAL_BOARD),
        "current_player": 0,
        "move_count": 0,
        "halfmove_clock": 0,
        "history": []
    }

# Function to apply an action and return the new state
def apply_action(state: State, action: Action) -> State:
    new_state = {
        "board": copy_board(state["board"]),
        "current_player": 1 - state["current_player"],
        "move_count": state["move_count"] + 1,
        "halfmove_clock": state["halfmove_clock"],
        "history": state["history"] + [action]
    }
    
    piece, from_square, to_square, *promotion = action.split('_')
    from_rank, from_file = int(from_square[1]) - 1, ord(from_square[0]) - ord('a')
    to_rank, to_file = int(to_square[1]) - 1, ord(to_square[0]) - ord('a')
    
    # Move the piece
    new_state["board"][to_rank][to_file] = new_state["board"][from_rank][from_file]
    new_state["board"][from_rank][from_file] = '.'
    
    # Handle promotion
    if promotion:
        new_state["board"][to_rank][to_file] = promotion[0]
    
    # Update halfmove clock
    if piece.lower() == 'p' or new_state["board"][to_rank][to_file] != '.':
        new_state["halfmove_clock"] = 0
    else:
        new_state["halfmove_clock"] += 1
    
    return new_state

# Function to get the current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Function to get the player name
def get_player_name(player_id: int) -> str:
    return PLAYER_NAMES[player_id]

# Function to get rewards
def get_rewards(state: State) -> List[float]:
    # Check for checkmate or stalemate
    if is_checkmate(state):
        return [1.0, -1.0] if state["current_player"] == 1 else [-1.0, 1.0]
    elif is_stalemate(state):
        return [0.5, 0.5]
    else:
        return [0.0, 0.0]

# Function to get legal actions
def get_legal_actions(state: State) -> List[Action]:
    if is_terminal(state):
        return []
    return generate_legal_moves(state)

# Function to get observations
def get_observations(state: State) -> List[PlayerObservation]:
    return [{"board": state["board"], "current_player": state["current_player"]}] * 2

# Helper function to determine if the game is in a terminal state
def is_terminal(state: State) -> bool:
    return is_checkmate(state) or is_stalemate(state) or state["halfmove_clock"] >= 50

# Helper function to determine if the current player is in checkmate
def is_checkmate(state: State) -> bool:
    # Placeholder for checkmate detection logic
    return False

# Helper function to determine if the game is in stalemate
def is_stalemate(state: State) -> bool:
    # Placeholder for stalemate detection logic
    return False

# Helper function to generate legal moves
def generate_legal_moves(state: State) -> List[Action]:
    # Placeholder for move generation logic
    return []

# Note: The implementation of move generation, checkmate, and stalemate detection is complex
# and requires a detailed understanding of chess rules and algorithms. The above code provides
# a framework, but the actual logic for these functions needs to be implemented.