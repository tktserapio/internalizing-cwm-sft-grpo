import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to generate the initial state
def _initial_board():
    return {
        'board': [
            ['r', 'n', 'b', 'q', 'k'],
            ['p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K']
        ],
        'turn': 0,
        'winner': None,
        'checkmate': False,
        'stalemate': False,
        'en_passant_target': None,
        'promotions': {}
    }

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return _initial_board()

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Parse the action
    piece, from_square, to_square = action.split('_')
    from_row, from_col = from_square[1], from_square[0]
    to_row, to_col = to_square[1], to_square[0]
    
    # Convert file and rank to index
    from_index = 5 * (ord(from_col) - ord('a')) + (ord(from_row) - ord('1'))
    to_index = 5 * (ord(to_col) - ord('a')) + (ord(to_row) - ord('1'))
    
    # Get the piece at the from_index
    piece_at_from = state['board'][int(from_row)][ord(from_col) - ord('a')]
    
    # Update the board
    state['board'][int(from_row)][ord(from_col) - ord('a')] = '.'
    state['board'][int(to_row)][ord(to_col) - ord('a')] = piece_at_from
    
    # Handle promotions
    if piece == 'P' and abs(int(from_row) - int(to_row)) == 2:
        state['promotions'][piece_at_from] = to_square
        state['board'][int(to_row)][ord(to_col) - ord('a')] = 'P'
    
    # Handle en passant
    if piece == 'P' and abs(int(from_row) - int(to_row)) == 1:
        if state['en_passant_target'] is not None:
            state['board'][int(state['en_passant_target'][1])][ord(state['en_passant_target'][0]) - ord('a')] = '.'
            state['en_passant_target'] = None
    
    # Handle castling
    if piece == 'R':
        if from_row == '1' and to_row == '5':
            state['board'][int('5')][ord('c') - ord('a')] = 'R'
            state['board'][int('5')][ord('g') - ord('a')] = 'R'
        elif from_row == '5' and to_row == '1':
            state['board'][int('1')][ord('c') - ord('a')] = 'R'
            state['board'][int('1')][ord('g') - ord('a')] = 'R'
    
    # Update the turn
    state['turn'] = 1 - state['turn']
    
    # Check for checkmate/stalemate
    if checkmate(state):
        state['winner'] = state['turn']
        state['checkmate'] = True
    elif stalemate(state):
        state['stalemate'] = True
    
    return state

def checkmate(state: State) -> bool:
    """Checks if the current player is in checkmate."""
    king_row, king_col = find_king(state)
    for row in range(5):
        for col in range(5):
            if state['board'][row][col] != '.':
                piece = state['board'][row][col]
                if piece in ('N', 'B', 'Q'):
                    if move_checkmate(state, piece, row, col, king_row, king_col):
                        return True
                elif piece == 'P':
                    if move_checkmate(state, piece, row, col, king_row, king_col):
                        return True
    return False

def move_checkmate(state: State, piece: str, row: int, col: int, king_row: int, king_col: int) -> bool:
    """Checks if a move by the given piece would result in checkmate."""
    for move in get_possible_moves(state, piece, row, col):
        new_state = apply_action(state.copy(), f"{piece}_{move}")
        if checkmate(new_state):
            return True
    return False

def find_king(state: State) -> tuple[int, int]:
    """Finds the coordinates of the king for the current player."""
    for row in range(5):
        for col in range(5):
            if state['board'][row][col] == 'K' and state['turn'] == 0:
                return row, col
            elif state['board'][row][col] == 'k' and state['turn'] == 1:
                return row, col

def get_possible_moves(state: State, piece: str, row: int, col: int) -> List[str]:
    """Generates possible moves for the given piece at the given position."""
    moves = []
    if piece == 'K':
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr != 0 or dc != 0:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] == '.':
                        moves.append(f"{piece}_{chr(ord('a') + new_col)}_{chr(ord('a') + col)}")
    elif piece == 'N':
        for dr in [-2, -1, 1, 2]:
            for dc in [-2, -1, 1, 2]:
                if dr != 0 or dc != 0:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] != '.':
                        moves.append(f"{piece}_{chr(ord('a') + new_col)}_{chr(ord('a') + col)}")
    elif piece == 'B':
        for dr in [-1, 1]:
            for dc in [-1, 1]:
                new_row, new_col = row + dr, col + dc
                while 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] == '.':
                    moves.append(f"{piece}_{chr(ord('a') + new_col)}_{chr(ord('a') + col)}")
                    new_row += dr
                    new_col += dc
                    if 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] != '.':
                        moves.append(f"{piece}_{chr(ord('a') + new_col)}_{chr(ord('a') + col)}")
                        break
    elif piece == 'R':
        for dr in [-1, 1]:
            new_row = row + dr
            while 0 <= new_row < 5 and state['board'][new_row][col] == '.':
                moves.append(f"{piece}_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                new_row += dr
            if 0 <= new_row < 5 and state['board'][new_row][col] != '.':
                moves.append(f"{piece}_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
    elif piece == 'Q':
        for dr in [-1, 1]:
            for dc in [-1, 1]:
                new_row, new_col = row + dr, col + dc
                while 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] == '.':
                    moves.append(f"{piece}_{chr(ord('a') + new_col)}_{chr(ord('a') + col)}")
                    new_row += dr
                    new_col += dc
                    if 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] != '.':
                        moves.append(f"{piece}_{chr(ord('a') + new_col)}_{chr(ord('a') + col)}")
                        break
    elif piece == 'P':
        if piece == 'P' and row == '1':
            if state['board'][int('2')][col] == '.':
                moves.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col)}_Q")
            if state['board'][int('3')][col] == '.':
                moves.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col)}_R")
        if piece == 'P' and row == '5':
            if state['board'][int('4')][col] == '.':
                moves.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col)}_Q")
            if state['board'][int('4')][col] == '.':
                moves.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col)}_R")
        if piece == 'P' and row == '2':
            if state['board'][int('3')][col] == 'P':
                moves.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col)}_P")
        if piece == 'P' and row == '4':
            if state['board'][int('3')][col] == 'P':
                moves.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col)}_P")
        if piece == 'P' and row == '3':
            if state['board'][int('2')][col] == 'P':
                moves.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col)}_P")
            if state['board'][int('4')][col] == 'P':
                moves.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col)}_P")
            if state['board'][int('4')][col] == 'P':
                moves.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col)}_P")
            if state['board'][int('5')][col] == 'P':
                moves.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col)}_P")
    return moves

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['turn']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['winner'] is not None:
        return [1.0, -1.0] if state['winner'] == 0 else [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['checkmate']:
        return []
    if state['stalemate']:
        return []
    return get_possible_moves(state, 'K', '1', 'a')

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{'board': state['board'], 'turn': state['turn']} for _ in range(2)]