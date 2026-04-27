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
PLAYER_WHITE = 0
PLAYER_BLACK = 1
EMPTY = '.'

# Initial board setup
INITIAL_BOARD = [
    ['r', 'n', 'b', 'q', 'k'],
    ['p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K']
]

# Helper function to clone the board
def clone_board(board: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in board]

# Helper function to convert board coordinates to algebraic notation
def to_algebraic(row: int, col: int) -> str:
    return f"{chr(col + ord('a'))}{5 - row}"

# Helper function to convert algebraic notation to board coordinates
def from_algebraic(pos: str) -> (int, int):
    col = ord(pos[0]) - ord('a')
    row = 5 - int(pos[1])
    return row, col

# Function to get the initial state
def get_initial_state() -> State:
    return {
        'board': clone_board(INITIAL_BOARD),
        'current_player': PLAYER_WHITE,
        'move_count': 0,
        'halfmove_clock': 0,
        'terminal': False
    }

# Function to apply an action and return the new state
def apply_action(state: State, action: Action) -> State:
    new_state = {
        'board': clone_board(state['board']),
        'current_player': 1 - state['current_player'],
        'move_count': state['move_count'] + 1,
        'halfmove_clock': state['halfmove_clock'],
        'terminal': False
    }
    
    # Parse the action
    parts = action.split('_')
    piece, from_pos, to_pos = parts[0], parts[1], parts[2]
    promotion = parts[3] if len(parts) == 4 else None
    
    from_row, from_col = from_algebraic(from_pos)
    to_row, to_col = from_algebraic(to_pos)
    
    # Move the piece
    new_state['board'][to_row][to_col] = new_state['board'][from_row][from_col]
    new_state['board'][from_row][from_col] = EMPTY
    
    # Handle promotion
    if promotion:
        new_state['board'][to_row][to_col] = promotion
    
    # Update halfmove clock
    if piece.lower() == 'p' or state['board'][to_row][to_col] != EMPTY:
        new_state['halfmove_clock'] = 0
    else:
        new_state['halfmove_clock'] += 1
    
    # Check for terminal state (checkmate or stalemate)
    if is_checkmate(new_state):
        new_state['terminal'] = True
    elif is_stalemate(new_state):
        new_state['terminal'] = True
    
    return new_state

# Function to get the current player
def get_current_player(state: State) -> int:
    return -4 if state['terminal'] else state['current_player']

# Function to get the player name
def get_player_name(player_id: int) -> str:
    return "White" if player_id == PLAYER_WHITE else "Black"

# Function to get the rewards
def get_rewards(state: State) -> List[float]:
    if not state['terminal']:
        return [0.0, 0.0]
    
    if is_checkmate(state):
        winner = 1 - state['current_player']
        return [1.0, -1.0] if winner == PLAYER_WHITE else [-1.0, 1.0]
    
    # Stalemate or draw conditions
    return [0.0, 0.0]

# Function to get legal actions
def get_legal_actions(state: State) -> List[Action]:
    if state['terminal']:
        return []
    
    legal_actions = []
    # Iterate over the board to find pieces of the current player
    for row in range(5):
        for col in range(5):
            piece = state['board'][row][col]
            if piece != EMPTY and ((piece.isupper() and state['current_player'] == PLAYER_WHITE) or
                                   (piece.islower() and state['current_player'] == PLAYER_BLACK)):
                legal_actions.extend(get_piece_legal_moves(state, row, col))
    
    return legal_actions

# Function to get observations
def get_observations(state: State) -> List[PlayerObservation]:
    return [{'board': state['board'], 'current_player': state['current_player']}] * 2

# Helper function to determine if the current state is checkmate
def is_checkmate(state: State) -> bool:
    # Check if the current player is in check and has no legal moves
    return is_in_check(state, state['current_player']) and not get_legal_actions(state)

# Helper function to determine if the current state is stalemate
def is_stalemate(state: State) -> bool:
    # Check if the current player is not in check but has no legal moves
    return not is_in_check(state, state['current_player']) and not get_legal_actions(state)

# Helper function to determine if a player is in check
def is_in_check(state: State, player: int) -> bool:
    # Find the king's position
    king = 'K' if player == PLAYER_WHITE else 'k'
    king_pos = None
    for row in range(5):
        for col in range(5):
            if state['board'][row][col] == king:
                king_pos = (row, col)
                break
        if king_pos:
            break
    
    # Check if any opponent piece can attack the king
    opponent = 1 - player
    for row in range(5):
        for col in range(5):
            piece = state['board'][row][col]
            if piece != EMPTY and ((piece.isupper() and opponent == PLAYER_WHITE) or
                                   (piece.islower() and opponent == PLAYER_BLACK)):
                if can_attack(state, row, col, king_pos[0], king_pos[1]):
                    return True
    return False

# Helper function to check if a piece can attack a position
def can_attack(state: State, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    # Implement attack logic based on piece type
    # This function should check if a piece at (from_row, from_col) can attack (to_row, to_col)
    return False  # Placeholder

# Helper function to get legal moves for a piece
def get_piece_legal_moves(state: State, row: int, col: int) -> List[Action]:
    # Implement logic to generate legal moves for a piece at (row, col)
    # This function should return a list of actions in the specified format
    return []  # Placeholder

# Note: The implementation of `can_attack` and `get_piece_legal_moves` is complex and requires handling each piece's movement rules.
# These functions are placeholders and need to be implemented to complete the game logic.