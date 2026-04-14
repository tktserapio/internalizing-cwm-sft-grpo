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

# Constants for the game
WHITE = 0
BLACK = 1
EMPTY = '.'
INITIAL_BOARD = [
    ['r', 'n', 'b', 'q', 'k'],
    ['p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K']
]

# Helper function to create a deep copy of the board
def copy_board(board: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in board]

# Helper function to convert board position to coordinates
def pos_to_coords(pos: str) -> (int, int):
    file, rank = pos
    return int(rank) - 1, ord(file) - ord('a')

# Helper function to convert coordinates to board position
def coords_to_pos(row: int, col: int) -> str:
    return f"{chr(col + ord('a'))}{row + 1}"

# Initialize the game state
def get_initial_state() -> State:
    return {
        'board': copy_board(INITIAL_BOARD),
        'current_player': WHITE,
        'move_count': 0,
        'last_pawn_move_or_capture': 0,
        'is_terminal': False,
        'winner': None
    }

# Determine the current player
def get_current_player(state: State) -> int:
    if state['is_terminal']:
        return -4
    return state['current_player']

# Get player name
def get_player_name(player_id: int) -> str:
    return "White" if player_id == WHITE else "Black"

# Get rewards for the current state
def get_rewards(state: State) -> List[float]:
    if not state['is_terminal']:
        return [0.0, 0.0]
    if state['winner'] == WHITE:
        return [1.0, -1.0]
    elif state['winner'] == BLACK:
        return [-1.0, 1.0]
    return [0.0, 0.0]  # In case of a draw

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = {
        'board': copy_board(state['board']),
        'current_player': 1 - state['current_player'],
        'move_count': state['move_count'] + 1,
        'last_pawn_move_or_capture': state['last_pawn_move_or_capture'],
        'is_terminal': False,
        'winner': None
    }
    
    # Parse the action
    parts = action.split('_')
    piece, from_pos, to_pos = parts[:3]
    promotion = parts[3] if len(parts) == 4 else None
    
    from_row, from_col = pos_to_coords(from_pos)
    to_row, to_col = pos_to_coords(to_pos)
    
    # Move the piece
    new_state['board'][to_row][to_col] = new_state['board'][from_row][from_col]
    new_state['board'][from_row][from_col] = EMPTY
    
    # Handle promotion
    if promotion:
        new_state['board'][to_row][to_col] = promotion
    
    # Update last pawn move or capture
    if piece.upper() == 'P' or new_state['board'][to_row][to_col].lower() in 'rnbqkp':
        new_state['last_pawn_move_or_capture'] = new_state['move_count']
    
    # Check for terminal state
    if is_checkmate(new_state):
        new_state['is_terminal'] = True
        new_state['winner'] = state['current_player']
    elif is_stalemate(new_state):
        new_state['is_terminal'] = True
        new_state['winner'] = None
    elif new_state['move_count'] - new_state['last_pawn_move_or_capture'] >= 50:
        new_state['is_terminal'] = True
        new_state['winner'] = None
    
    return new_state

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state['is_terminal']:
        return []
    
    # Generate all legal moves for the current player
    legal_actions = []
    for row in range(5):
        for col in range(5):
            piece = state['board'][row][col]
            if piece == EMPTY or (state['current_player'] == WHITE and piece.islower()) or (state['current_player'] == BLACK and piece.isupper()):
                continue
            legal_actions.extend(generate_legal_moves(state, row, col))
    
    return legal_actions

# Generate legal moves for a piece at a given position
def generate_legal_moves(state: State, row: int, col: int) -> List[Action]:
    piece = state['board'][row][col]
    moves = []
    if piece.upper() == 'P':
        moves.extend(generate_pawn_moves(state, row, col))
    elif piece.upper() == 'N':
        moves.extend(generate_knight_moves(state, row, col))
    elif piece.upper() == 'B':
        moves.extend(generate_bishop_moves(state, row, col))
    elif piece.upper() == 'R':
        moves.extend(generate_rook_moves(state, row, col))
    elif piece.upper() == 'Q':
        moves.extend(generate_queen_moves(state, row, col))
    elif piece.upper() == 'K':
        moves.extend(generate_king_moves(state, row, col))
    return moves

# Generate legal pawn moves
def generate_pawn_moves(state: State, row: int, col: int) -> List[Action]:
    # Implement pawn movement logic
    # This is a placeholder; actual implementation would handle moves, captures, promotions, and en passant
    return []

# Generate legal knight moves
def generate_knight_moves(state: State, row: int, col: int) -> List[Action]:
    # Implement knight movement logic
    # This is a placeholder; actual implementation would handle the L-shaped moves
    return []

# Generate legal bishop moves
def generate_bishop_moves(state: State, row: int, col: int) -> List[Action]:
    # Implement bishop movement logic
    # This is a placeholder; actual implementation would handle diagonal moves
    return []

# Generate legal rook moves
def generate_rook_moves(state: State, row: int, col: int) -> List[Action]:
    # Implement rook movement logic
    # This is a placeholder; actual implementation would handle horizontal and vertical moves
    return []

# Generate legal queen moves
def generate_queen_moves(state: State, row: int, col: int) -> List[Action]:
    # Implement queen movement logic
    # This is a placeholder; actual implementation would combine rook and bishop moves
    return []

# Generate legal king moves
def generate_king_moves(state: State, row: int, col: int) -> List[Action]:
    # Implement king movement logic
    # This is a placeholder; actual implementation would handle one-square moves in any direction
    return []

# Check if the current player is in checkmate
def is_checkmate(state: State) -> bool:
    # Implement checkmate detection logic
    # This is a placeholder; actual implementation would verify if the king is in check and has no legal moves
    return False

# Check if the current player is in stalemate
def is_stalemate(state: State) -> bool:
    # Implement stalemate detection logic
    # This is a placeholder; actual implementation would verify if the player has no legal moves but is not in check
    return False

# Get observations for both players
def get_observations(state: State) -> List[PlayerObservation]:
    return [state, state]  # Perfect information game, both players see the same state