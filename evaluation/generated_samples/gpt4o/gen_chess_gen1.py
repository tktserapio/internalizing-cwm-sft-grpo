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
WHITE = 0
BLACK = 1

# Initial board setup
INITIAL_BOARD = [
    ["r", "n", "b", "q", "k"],  # Black pieces
    ["p", "p", "p", "p", "p"],  # Black pawns
    [".", ".", ".", ".", "."],  # Empty row
    ["P", "P", "P", "P", "P"],  # White pawns
    ["R", "N", "B", "Q", "K"]   # White pieces
]

# Helper function to create a deep copy of the board
def copy_board(board: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in board]

# Convert board coordinates to algebraic notation
def coord_to_algebraic(x: int, y: int) -> str:
    return chr(ord('a') + x) + str(5 - y)

# Convert algebraic notation to board coordinates
def algebraic_to_coord(pos: str) -> (int, int):
    return ord(pos[0]) - ord('a'), 5 - int(pos[1])

# Initialize the game state
def get_initial_state() -> State:
    return {
        "board": copy_board(INITIAL_BOARD),
        "current_player": WHITE,
        "halfmove_clock": 0,
        "fullmove_number": 1,
        "terminal": False,
        "winner": None
    }

# Get the current player
def get_current_player(state: State) -> int:
    return state["current_player"] if not state["terminal"] else -4

# Get the player name
def get_player_name(player_id: int) -> str:
    return "White" if player_id == WHITE else "Black"

# Check if a position is within the board boundaries
def is_within_bounds(x: int, y: int) -> bool:
    return 0 <= x < 5 and 0 <= y < 5

# Determine if a move is legal
def is_legal_move(state: State, action: Action) -> bool:
    # Parse the action
    parts = action.split('_')
    piece = parts[0]
    from_pos = parts[1]
    to_pos = parts[2]
    # Convert positions to coordinates
    from_x, from_y = algebraic_to_coord(from_pos)
    to_x, to_y = algebraic_to_coord(to_pos)
    # Check if move is within bounds
    if not (is_within_bounds(from_x, from_y) and is_within_bounds(to_x, to_y)):
        return False
    # Additional logic to check if the move is valid according to chess rules
    # This includes checking for piece-specific movement rules, captures, etc.
    # For simplicity, this function will be expanded with specific rules for each piece
    return True

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    if state["terminal"]:
        return state
    
    new_state = {
        "board": copy_board(state["board"]),
        "current_player": 1 - state["current_player"],
        "halfmove_clock": state["halfmove_clock"] + 1,
        "fullmove_number": state["fullmove_number"] + (1 if state["current_player"] == BLACK else 0),
        "terminal": False,
        "winner": None
    }
    
    # Parse the action
    parts = action.split('_')
    piece = parts[0]
    from_pos = parts[1]
    to_pos = parts[2]
    # Convert positions to coordinates
    from_x, from_y = algebraic_to_coord(from_pos)
    to_x, to_y = algebraic_to_coord(to_pos)
    
    # Move the piece
    new_state["board"][to_y][to_x] = new_state["board"][from_y][from_x]
    new_state["board"][from_y][from_x] = "."
    
    # Check for pawn promotion
    if piece == "P" and (to_y == 0 or to_y == 4):
        promotion_piece = parts[3] if len(parts) > 3 else "Q"
        new_state["board"][to_y][to_x] = promotion_piece
    
    # Check for checkmate, stalemate, etc., and update terminal state and winner
    # This logic will be expanded to handle these conditions
    
    return new_state

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state["terminal"]:
        return []
    
    legal_actions = []
    # Generate all possible moves for the current player
    # This involves iterating over the board, identifying pieces, and generating moves
    # For simplicity, this function will be expanded with specific rules for each piece
    return legal_actions

# Get the rewards for the current state
def get_rewards(state: State) -> List[float]:
    if state["terminal"]:
        if state["winner"] == WHITE:
            return [1.0, -1.0]
        elif state["winner"] == BLACK:
            return [-1.0, 1.0]
        else:
            return [0.0, 0.0]  # Draw
    return [0.0, 0.0]

# Get the observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    return [{"board": state["board"], "current_player": state["current_player"]}] * 2

# The above code sets up the basic framework for the game. The functions for move legality, 
# checkmate detection, and specific piece movements need to be implemented in detail.