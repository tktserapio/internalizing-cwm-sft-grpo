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
WHITE, BLACK = 0, 1
EMPTY = '.'
INITIAL_BOARD = [
    ['r', 'n', 'b', 'q', 'k'],
    ['p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K']
]

# Helper functions
def is_within_bounds(x: int, y: int) -> bool:
    """Check if the given coordinates are within the board boundaries."""
    return 0 <= x < 5 and 0 <= y < 5

def get_piece_color(piece: str) -> int:
    """Return the color of the piece: WHITE or BLACK."""
    if piece.isupper():
        return WHITE
    elif piece.islower():
        return BLACK
    return -1

def algebraic_to_index(pos: str) -> Tuple[int, int]:
    """Convert algebraic notation to board indices."""
    file, rank = pos
    return 5 - int(rank), ord(file) - ord('a')

def index_to_algebraic(x: int, y: int) -> str:
    """Convert board indices to algebraic notation."""
    return f"{chr(y + ord('a'))}{5 - x}"

def is_opponent_piece(piece: str, player: int) -> bool:
    """Check if the piece belongs to the opponent."""
    return (player == WHITE and piece.islower()) or (player == BLACK and piece.isupper())

def is_empty_square(piece: str) -> bool:
    """Check if the square is empty."""
    return piece == EMPTY

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
        'halfmove_clock': state['halfmove_clock'],
        'history': state['history'] + [action]
    }
    
    # Parse the action
    parts = action.split('_')
    piece, from_pos, to_pos = parts[0], parts[1], parts[2]
    promotion = parts[3] if len(parts) == 4 else None
    
    from_x, from_y = algebraic_to_index(from_pos)
    to_x, to_y = algebraic_to_index(to_pos)
    
    # Move the piece
    new_state['board'][to_x][to_y] = new_state['board'][from_x][from_y]
    new_state['board'][from_x][from_y] = EMPTY
    
    # Handle promotion
    if promotion:
        new_state['board'][to_x][to_y] = promotion if state['current_player'] == WHITE else promotion.lower()
    
    # Update halfmove clock
    if piece.upper() == 'P' or not is_empty_square(state['board'][to_x][to_y]):
        new_state['halfmove_clock'] = 0
    else:
        new_state['halfmove_clock'] += 1
    
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
    if is_checkmate(state):
        winner = 1 - state['current_player']
        return [1.0, -1.0] if winner == WHITE else [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if is_terminal(state):
        return []
    
    legal_actions = []
    board = state['board']
    player = state['current_player']
    
    for x in range(5):
        for y in range(5):
            piece = board[x][y]
            if get_piece_color(piece) == player:
                legal_actions.extend(get_piece_legal_moves(board, piece, x, y, player))
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

def is_terminal(state: State) -> bool:
    """Check if the game is in a terminal state."""
    return is_checkmate(state) or is_stalemate(state) or state['halfmove_clock'] >= 50

def is_checkmate(state: State) -> bool:
    """Check if the current player is in checkmate."""
    # Implement checkmate detection logic here
    return False

def is_stalemate(state: State) -> bool:
    """Check if the game is in stalemate."""
    # Implement stalemate detection logic here
    return False

def get_piece_legal_moves(board: List[List[str]], piece: str, x: int, y: int, player: int) -> List[Action]:
    """Get all legal moves for a piece at a given position."""
    moves = []
    if piece.upper() == 'P':
        moves.extend(get_pawn_moves(board, x, y, player))
    elif piece.upper() == 'N':
        moves.extend(get_knight_moves(board, x, y, player))
    elif piece.upper() == 'B':
        moves.extend(get_bishop_moves(board, x, y, player))
    elif piece.upper() == 'R':
        moves.extend(get_rook_moves(board, x, y, player))
    elif piece.upper() == 'Q':
        moves.extend(get_queen_moves(board, x, y, player))
    elif piece.upper() == 'K':
        moves.extend(get_king_moves(board, x, y, player))
    return moves

def get_pawn_moves(board: List[List[str]], x: int, y: int, player: int) -> List[Action]:
    """Get all legal pawn moves."""
    moves = []
    direction = -1 if player == WHITE else 1
    start_rank = 3 if player == WHITE else 1
    promotion_rank = 0 if player == WHITE else 4
    
    # Forward move
    if is_within_bounds(x + direction, y) and is_empty_square(board[x + direction][y]):
        if x + direction == promotion_rank:
            for promo in ['Q', 'R', 'B', 'N']:
                moves.append(f"P_{index_to_algebraic(x, y)}_{index_to_algebraic(x + direction, y)}_{promo}")
        else:
            moves.append(f"P_{index_to_algebraic(x, y)}_{index_to_algebraic(x + direction, y)}")
        
        # Double move from start
        if x == start_rank and is_empty_square(board[x + 2 * direction][y]):
            moves.append(f"P_{index_to_algebraic(x, y)}_{index_to_algebraic(x + 2 * direction, y)}")
    
    # Captures
    for dy in [-1, 1]:
        if is_within_bounds(x + direction, y + dy) and is_opponent_piece(board[x + direction][y + dy], player):
            if x + direction == promotion_rank:
                for promo in ['Q', 'R', 'B', 'N']:
                    moves.append(f"P_{index_to_algebraic(x, y)}_{index_to_algebraic(x + direction, y + dy)}_{promo}")
            else:
                moves.append(f"P_{index_to_algebraic(x, y)}_{index_to_algebraic(x + direction, y + dy)}")
    
    return moves

def get_knight_moves(board: List[List[str]], x: int, y: int, player: int) -> List[Action]:
    """Get all legal knight moves."""
    moves = []
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    
    for dx, dy in knight_moves:
        nx, ny = x + dx, y + dy
        if is_within_bounds(nx, ny) and (is_empty_square(board[nx][ny]) or is_opponent_piece(board[nx][ny], player)):
            moves.append(f"N_{index_to_algebraic(x, y)}_{index_to_algebraic(nx, ny)}")
    
    return moves

def get_bishop_moves(board: List[List[str]], x: int, y: int, player: int) -> List[Action]:
    """Get all legal bishop moves."""
    return get_sliding_moves(board, x, y, player, [(1, 1), (1, -1), (-1, 1), (-1, -1)])

def get_rook_moves(board: List[List[str]], x: int, y: int, player: int) -> List[Action]:
    """Get all legal rook moves."""
    return get_sliding_moves(board, x, y, player, [(1, 0), (-1, 0), (0, 1), (0, -1)])

def get_queen_moves(board: List[List[str]], x: int, y: int, player: int) -> List[Action]:
    """Get all legal queen moves."""
    return get_sliding_moves(board, x, y, player, [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)])

def get_king_moves(board: List[List[str]], x: int, y: int, player: int) -> List[Action]:
    """Get all legal king moves."""
    moves = []
    king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    for dx, dy in king_moves:
        nx, ny = x + dx, y + dy
        if is_within_bounds(nx, ny) and (is_empty_square(board[nx][ny]) or is_opponent_piece(board[nx][ny], player)):
            moves.append(f"K_{index_to_algebraic(x, y)}_{index_to_algebraic(nx, ny)}")
    
    return moves

def get_sliding_moves(board: List[List[str]], x: int, y: int, player: int, directions: List[Tuple[int, int]]) -> List[Action]:
    """Get all legal sliding moves for a piece."""
    moves = []
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        while is_within_bounds(nx, ny):
            if is_empty_square(board[nx][ny]):
                moves.append(f"{board[x][y].upper()}_{index_to_algebraic(x, y)}_{index_to_algebraic(nx, ny)}")
            elif is_opponent_piece(board[nx][ny], player):
                moves.append(f"{board[x][y].upper()}_{index_to_algebraic(x, y)}_{index_to_algebraic(nx, ny)}")
                break
            else:
                break
            nx += dx
            ny += dy
    
    return moves