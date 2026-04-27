import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Dict, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
INITIAL_BOARD = [
    ['r', 'n', 'b', 'q', 'k'],
    ['p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K']
]

PIECE_MOVES = {
    'P': [(1, 0), (2, 0)],  # Pawn moves
    'N': [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)],  # Knight moves
    'B': [(1, 1), (1, -1), (-1, 1), (-1, -1)],  # Bishop moves
    'R': [(1, 0), (0, 1), (-1, 0), (0, -1)],  # Rook moves
    'Q': [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],  # Queen moves
    'K': [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # King moves
}

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [row[:] for row in INITIAL_BOARD],
        'current_player': 0,
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
    piece, from_square, to_square = parts[0], parts[1], parts[2]
    from_rank, from_file = int(from_square[1]) - 1, ord(from_square[0]) - ord('a')
    to_rank, to_file = int(to_square[1]) - 1, ord(to_square[0]) - ord('a')

    # Move the piece
    new_state['board'][to_rank][to_file] = new_state['board'][from_rank][from_file]
    new_state['board'][from_rank][from_file] = '.'

    # Handle promotion
    if len(parts) == 4:
        promotion_piece = parts[3]
        new_state['board'][to_rank][to_file] = promotion_piece

    # Update halfmove clock
    if piece.upper() == 'P' or new_state['board'][to_rank][to_file] != '.':
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
    return "White" if player_id == 0 else "Black"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if is_terminal(state):
        winner = get_winner(state)
        if winner == 0:
            return [1.0, -1.0]
        elif winner == 1:
            return [-1.0, 1.0]
        else:
            return [0.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if is_terminal(state):
        return []

    legal_actions = []
    current_player = state['current_player']
    for rank in range(5):
        for file in range(5):
            piece = state['board'][rank][file]
            if piece != '.' and (piece.isupper() == (current_player == 0)):
                legal_actions.extend(get_piece_legal_actions(state, piece, rank, file))
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{'board': state['board'], 'current_player': state['current_player']} for _ in range(2)]

def is_terminal(state: State) -> bool:
    """Check if the game is in a terminal state."""
    # Check for checkmate or stalemate
    if any(get_legal_actions(state)):
        return False
    return True

def get_winner(state: State) -> int:
    """Determine the winner of the game."""
    # Check if the current player is in checkmate
    if is_check(state, state['current_player']):
        return 1 - state['current_player']
    return -1  # Draw or stalemate

def is_check(state: State, player: int) -> bool:
    """Check if the given player's king is in check."""
    # Find the king's position
    king = 'K' if player == 0 else 'k'
    king_pos = None
    for rank in range(5):
        for file in range(5):
            if state['board'][rank][file] == king:
                king_pos = (rank, file)
                break
        if king_pos:
            break

    # Check if any opposing piece can attack the king
    opponent = 1 - player
    for rank in range(5):
        for file in range(5):
            piece = state['board'][rank][file]
            if piece != '.' and (piece.isupper() == (opponent == 0)):
                if can_attack(state, piece, rank, file, king_pos[0], king_pos[1]):
                    return True
    return False

def can_attack(state: State, piece: str, from_rank: int, from_file: int, to_rank: int, to_file: int) -> bool:
    """Check if a piece can attack a given position."""
    # Implement logic to check if the piece can move to the target position
    # This will involve checking the piece's movement rules and any obstacles
    return False

def get_piece_legal_actions(state: State, piece: str, rank: int, file: int) -> List[Action]:
    """Get all legal actions for a specific piece on the board."""
    legal_actions = []
    # Implement logic to generate legal moves for the piece
    return legal_actions

# Additional helper functions to implement movement logic, check for obstacles, etc., would be added here.