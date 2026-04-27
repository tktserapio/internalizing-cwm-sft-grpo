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

# Helper function to initialize the board
def initialize_board() -> List[List[str]]:
    return [
        ['r', 'n', 'b', 'q', 'k'],  # Black pieces
        ['p', 'p', 'p', 'p', 'p'],  # Black pawns
        ['.', '.', '.', '.', '.'],  # Empty row
        ['P', 'P', 'P', 'P', 'P'],  # White pawns
        ['R', 'N', 'B', 'Q', 'K']   # White pieces
    ]

# Helper function to convert board position to algebraic notation
def pos_to_algebraic(row: int, col: int) -> str:
    return f"{chr(col + ord('a'))}{5 - row}"

# Helper function to convert algebraic notation to board position
def algebraic_to_pos(algebraic: str) -> (int, int):
    col = ord(algebraic[0]) - ord('a')
    row = 5 - int(algebraic[1])
    return row, col

# Returns the initial game state before any actions are taken
def get_initial_state() -> State:
    return {
        'board': initialize_board(),
        'current_player': 0,
        'move_count': 0,
        'halfmove_clock': 0,
        'history': []
    }

# Returns current player (e.g. 0 or 1), or -4 for terminal state
def get_current_player(state: State) -> int:
    # Check for terminal state
    if is_terminal(state):
        return -4
    return state['current_player']

# Returns the name of the player
def get_player_name(player_id: int) -> str:
    return "White" if player_id == 0 else "Black"

# Returns the rewards per player
def get_rewards(state: State) -> List[float]:
    if is_terminal(state):
        winner = determine_winner(state)
        if winner == 0:
            return [1.0, -1.0]
        elif winner == 1:
            return [-1.0, 1.0]
        else:
            return [0.0, 0.0]  # Draw
    return [0.0, 0.0]

# Returns legal actions for current state. Empty list if terminal
def get_legal_actions(state: State) -> List[Action]:
    if is_terminal(state):
        return []
    # Generate legal moves for the current player
    return generate_legal_moves(state)

# Returns [player_0_obs, player_1_obs]
def get_observations(state: State) -> List[PlayerObservation]:
    return [state, state]  # Perfect information game

# Returns the new state after an action has been taken
def apply_action(state: State, action: Action) -> State:
    new_state = {
        'board': [row[:] for row in state['board']],  # Deep copy of the board
        'current_player': 1 - state['current_player'],
        'move_count': state['move_count'] + 1,
        'halfmove_clock': state['halfmove_clock'],
        'history': state['history'] + [action]
    }
    
    # Parse the action
    parts = action.split('_')
    piece, from_pos, to_pos = parts[0], parts[1], parts[2]
    from_row, from_col = algebraic_to_pos(from_pos)
    to_row, to_col = algebraic_to_pos(to_pos)
    
    # Move the piece
    new_state['board'][to_row][to_col] = new_state['board'][from_row][from_col]
    new_state['board'][from_row][from_col] = '.'
    
    # Handle pawn promotion
    if len(parts) == 4:
        promotion_piece = parts[3]
        new_state['board'][to_row][to_col] = promotion_piece.upper() if state['current_player'] == 0 else promotion_piece.lower()
    
    # Update halfmove clock
    if piece == 'P' or new_state['board'][to_row][to_col] != '.':
        new_state['halfmove_clock'] = 0
    else:
        new_state['halfmove_clock'] += 1
    
    return new_state

# Check if the game is in a terminal state
def is_terminal(state: State) -> bool:
    # Check for checkmate, stalemate, or draw conditions
    return determine_winner(state) is not None or state['halfmove_clock'] >= 50

# Determine the winner of the game
def determine_winner(state: State) -> int:
    # Check for checkmate or stalemate
    # Implement logic to determine if a player is in checkmate or if the game is a draw
    return None  # Placeholder

# Generate legal moves for the current player
def generate_legal_moves(state: State) -> List[Action]:
    # Implement logic to generate all legal moves for the current player
    return []  # Placeholder

# Note: The functions `determine_winner` and `generate_legal_moves` need to be fully implemented
# to handle the specific rules of chess, including check, checkmate, and stalemate detection.