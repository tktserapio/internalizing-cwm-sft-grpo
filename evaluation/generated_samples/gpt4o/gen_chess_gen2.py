import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants for player identification
WHITE = 0
BLACK = 1

# Initial board setup
INITIAL_BOARD = [
    ['r', 'n', 'b', 'q', 'k'],  # Black pieces
    ['p', 'p', 'p', 'p', 'p'],  # Black pawns
    ['.', '.', '.', '.', '.'],  # Empty row
    ['P', 'P', 'P', 'P', 'P'],  # White pawns
    ['R', 'N', 'B', 'Q', 'K']   # White pieces
]

# Directions for piece movements
DIRECTIONS = {
    'K': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
    'Q': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
    'R': [(1, 0), (-1, 0), (0, 1), (0, -1)],
    'B': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
    'N': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
    'P': [(1, 0), (1, 1), (1, -1)]  # Forward, capture diagonally
}

# Helper functions
def is_within_bounds(x: int, y: int) -> bool:
    """Check if a position is within the board boundaries."""
    return 0 <= x < 5 and 0 <= y < 5

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [row[:] for row in INITIAL_BOARD],
        'current_player': WHITE,
        'move_count': 0,
        'halfmove_clock': 0,
        'history': []
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        'board': [row[:] for row in state['board']],
        'current_player': 1 - state['current_player'],
        'move_count': state['move_count'] + 1,
        'halfmove_clock': state['halfmove_clock'] + 1,
        'history': state['history'] + [action]
    }

    # Parse the action
    parts = action.split('_')
    piece = parts[0]
    from_pos = parts[1]
    to_pos = parts[2]
    promotion = parts[3] if len(parts) > 3 else None

    from_x, from_y = algebraic_to_index(from_pos)
    to_x, to_y = algebraic_to_index(to_pos)

    # Move the piece
    new_state['board'][to_x][to_y] = new_state['board'][from_x][from_y]
    new_state['board'][from_x][from_y] = '.'

    # Handle pawn promotion
    if promotion:
        new_state['board'][to_x][to_y] = promotion

    # Reset halfmove clock if a pawn moved or a piece was captured
    if piece.upper() == 'P' or state['board'][to_x][to_y] != '.':
        new_state['halfmove_clock'] = 0

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if is_terminal(state):
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "White" if player_id == WHITE else "Black"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if is_terminal(state):
        winner = get_winner(state)
        if winner is None:
            return [0.5, 0.5]  # Draw
        return [1.0, 0.0] if winner == WHITE else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if is_terminal(state):
        return []

    legal_actions = []
    current_player = state['current_player']
    for x in range(5):
        for y in range(5):
            piece = state['board'][x][y]
            if piece == '.' or (current_player == WHITE and piece.islower()) or (current_player == BLACK and piece.isupper()):
                continue

            piece_type = piece.upper()
            directions = DIRECTIONS.get(piece_type, [])

            # Generate moves for each direction
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                while is_within_bounds(nx, ny):
                    target_piece = state['board'][nx][ny]
                    if target_piece == '.':
                        legal_actions.append(format_action(piece, x, y, nx, ny))
                    elif (current_player == WHITE and target_piece.islower()) or (current_player == BLACK and target_piece.isupper()):
                        legal_actions.append(format_action(piece, x, y, nx, ny))
                        break
                    else:
                        break

                    if piece_type in ['K', 'N', 'P']:  # Single step for King, Knight, Pawn
                        break

                    nx += dx
                    ny += dy

            # Handle pawn promotions
            if piece_type == 'P':
                promotion_rank = 4 if current_player == WHITE else 0
                if x == promotion_rank:
                    for promo_piece in ['Q', 'R', 'B', 'N']:
                        legal_actions.append(format_action(piece, x, y, nx, ny, promo_piece))

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

def algebraic_to_index(pos: str) -> Tuple[int, int]:
    """Converts algebraic notation to board indices."""
    file, rank = pos
    return 5 - int(rank), ord(file) - ord('a')

def format_action(piece: str, from_x: int, from_y: int, to_x: int, to_y: int, promo: str = None) -> Action:
    """Formats an action string."""
    from_pos = index_to_algebraic(from_x, from_y)
    to_pos = index_to_algebraic(to_x, to_y)
    if promo:
        return f"{piece}_{from_pos}_{to_pos}_{promo}"
    return f"{piece}_{from_pos}_{to_pos}"

def index_to_algebraic(x: int, y: int) -> str:
    """Converts board indices to algebraic notation."""
    return f"{chr(y + ord('a'))}{5 - x}"

def is_terminal(state: State) -> bool:
    """Determines if the game is in a terminal state."""
    # Check for checkmate or stalemate
    if not get_legal_actions(state):
        return True
    # Check for 50-move rule
    if state['halfmove_clock'] >= 50:
        return True
    return False

def get_winner(state: State) -> int:
    """Determines the winner of the game, if any."""
    if is_terminal(state):
        if not get_legal_actions(state):
            # Check if the current player is in check
            if is_in_check(state, state['current_player']):
                return 1 - state['current_player']
            return None  # Stalemate
    return None

def is_in_check(state: State, player: int) -> bool:
    """Checks if the given player's king is in check."""
    # Locate the king
    king_char = 'K' if player == WHITE else 'k'
    king_pos = None
    for x in range(5):
        for y in range(5):
            if state['board'][x][y] == king_char:
                king_pos = (x, y)
                break
        if king_pos:
            break

    if not king_pos:
        return False

    # Check if any opponent piece can attack the king
    opponent = 1 - player
    for x in range(5):
        for y in range(5):
            piece = state['board'][x][y]
            if piece == '.' or (opponent == WHITE and piece.islower()) or (opponent == BLACK and piece.isupper()):
                continue

            piece_type = piece.upper()
            directions = DIRECTIONS.get(piece_type, [])

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                while is_within_bounds(nx, ny):
                    if (nx, ny) == king_pos:
                        return True
                    if state['board'][nx][ny] != '.':
                        break
                    if piece_type in ['K', 'N', 'P']:  # Single step for King, Knight, Pawn
                        break
                    nx += dx
                    ny += dy

    return False