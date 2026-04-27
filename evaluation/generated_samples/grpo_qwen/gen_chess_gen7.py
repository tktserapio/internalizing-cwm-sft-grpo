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

# Helper function to convert algebraic notation to coordinates
def algebraic_to_coordinates(algebraic_notation: str) -> tuple[int, int]:
    file, rank = algebraic_notation
    file_index = 'abcdefgh'.index(file)
    rank_index = int(rank) - 1
    return file_index, rank_index

# Helper function to convert coordinates to algebraic notation
def coordinates_to_algebraic(file_index: int, rank_index: int) -> str:
    file = 'abcdefgh'[file_index]
    rank = str(rank_index + 1)
    return f"{file}{rank}"

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial board setup
    board = {
        'r': (4, 0),  # Rook
        'n': (4, 1),  # Knight
        'b': (4, 2),  # Bishop
        'q': (4, 3),  # Queen
        'k': (4, 4),  # King
        'p': [(1, i) for i in range(5)],  # Pawns
        'R': (0, 0),
        'N': (0, 1),
        'B': (0, 2),
        'Q': (0, 3),
        'K': (0, 4)
    }
    return {
        'board': board,
        'turn': 0,
        'castled': False,
        'en_passant_target': None,
        'en_passant_turn': None,
        'promoted_piece': None,
        'check': False,
        'checkmate': False,
        'stalemate': False,
        'material': {'W': 12, 'B': 12},
        'moves': 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    piece, from_square, to_square = action.split('_')
    from_file, from_rank = algebraic_to_coordinates(from_square)
    to_file, to_rank = algebraic_to_coordinates(to_square)
    
    # Convert to index-based coordinates for easier manipulation
    from_index = from_file + from_rank * 5
    to_index = to_file + to_rank * 5
    
    # Handle special cases like castling, en passant, and promotions
    if piece == 'P' and abs(to_rank - from_rank) == 2:
        new_state['en_passant_target'] = (to_file, to_rank - 1)
        new_state['en_passant_turn'] = state['turn']
        new_state['moves'] += 1
        new_state['material']['W'] -= 1
        new_state['material']['B'] -= 1
    elif piece == 'P' and to_rank == 0 or to_rank == 4:
        new_state['promoted_piece'] = piece
        new_state['promoted_piece_index'] = to_index
        new_state['material']['W'] -= 1
        new_state['material']['B'] -= 1
    else:
        new_state['board'][piece][from_index], new_state['board'][piece][to_index] = (
            new_state['board'][piece][to_index],
            new_state['board'][piece][from_index]
        )
        new_state['board'][piece][from_index] = None
        new_state['board'][piece][to_index] = piece
        
        # Update castling status if necessary
        if piece == 'K':
            if from_rank == 4 and to_rank == 2:
                new_state['castled'] = True
            elif from_rank == 2 and to_rank == 4:
                new_state['castled'] = True
            else:
                new_state['castled'] = False
        
        # Update en passant target if necessary
        if piece == 'P' and abs(to_rank - from_rank) == 2:
            new_state['board'][new_state['promoted_piece']][new_state['en_passant_target']] = None
            new_state['promoted_piece'] = None
            new_state['en_passant_target'] = None
            new_state['en_passant_turn'] = None
            new_state['moves'] += 1
            new_state['material']['W'] -= 1
            new_state['material']['B'] -= 1
        
        # Update check and checkmate status
        new_state['check'], new_state['checkmate'], new_state['stalemate'] = check_and_update_checkmate(new_state)
        
        # Increment move count
        new_state['moves'] += 1
        
    # Update turn
    new_state['turn'] = (state['turn'] + 1) % 2
    
    return new_state

def check_and_update_checkmate(state: State) -> tuple[bool, bool, bool]:
    """
    Checks if the current player is in check, checkmate, or stalemate.
    Updates the state accordingly.
    """
    king_pos = next((file, rank) for file, rank in state['board'].items() if rank == 4)
    king_file, king_rank = algebraic_to_coordinates(king_pos)
    
    # Check if the opponent has a piece that can capture the king
    for piece, pos in state['board'].items():
        if piece != 'K' and pos is not None:
            piece_file, piece_rank = algebraic_to_coordinates(pos)
            if abs(piece_file - king_file) <= 1 and abs(piece_rank - king_rank) <= 1:
                return False, False, False  # Not in check
    
    # Check if the opponent has a move that puts the king in check
    for piece, pos in state['board'].items():
        if piece != 'K' and pos is not None:
            piece_file, piece_rank = algebraic_to_coordinates(pos)
            for move in get_possible_moves(state):
                if move == f'{piece}_{coordinates_to_algebraic(piece_file, piece_rank)}_{coordinates_to_algebraic(king_file, king_rank)}':
                    return False, False, False  # Not in check
    
    # Check if the opponent has a move that puts the king in checkmate
    for piece, pos in state['board'].items():
        if piece != 'K' and pos is not None:
            piece_file, piece_rank = algebraic_to_coordinates(pos)
            for move in get_possible_moves(state):
                if move == f'{piece}_{coordinates_to_algebraic(piece_file, piece_rank)}_{coordinates_to_algebraic(king_file, king_rank)}':
                    return False, True, False  # In checkmate
    
    # Check if the opponent has a move that puts the king in stalemate
    for piece, pos in state['board'].items():
        if piece != 'K' and pos is not None:
            piece_file, piece_rank = algebraic_to_coordinates(pos)
            for move in get_possible_moves(state):
                if move == f'{piece}_{coordinates_to_algebraic(piece_file, piece_rank)}_{coordinates_to_algebraic(king_file, king_rank)}':
                    return False, False, True  # In stalemate
    
    return True, False, False  # In check

def get_possible_moves(state: State) -> List[str]:
    """
    Returns a list of possible moves for the current player.
    """
    moves = []
    for piece, pos in state['board'].items():
        if piece != 'K' and pos is not None:
            piece_file, piece_rank = algebraic_to_coordinates(pos)
            for move in get_possible_moves_for_piece(piece, piece_file, piece_rank, state):
                moves.append(f'{piece}_{coordinates_to_algebraic(piece_file, piece_rank)}_{coordinates_to_algebraic(move[0], move[1])}')
    return moves

def get_possible_moves_for_piece(piece: str, file: int, rank: int, state: State) -> List[tuple[int, int]]:
    """
    Returns a list of possible moves for a given piece at a given position.
    """
    if piece == 'P':
        if state['turn'] == 0 and rank == 1:
            yield (file, rank + 2)
        elif state['turn'] == 1 and rank == 4:
            yield (file, rank - 2)
        else:
            yield (file, rank + 1)
            yield (file, rank - 1)
    elif piece == 'R':
        for delta in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for step in range(1, 5):
                new_file, new_rank = file + delta[0] * step, rank + delta[1] * step
                if 0 <= new_file < 5 and 0 <= new_rank < 5 and state['board'][piece][new_file, new_rank] is None:
                    yield (new_file, new_rank)
                elif state['board'][piece][new_file, new_rank] is not None:
                    break
    elif piece == 'N':
        for delta in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            new_file, new_rank = file + delta[0], rank + delta[1]
            if 0 <= new_file < 5 and 0 <= new_rank < 5 and state['board'][piece][new_file, new_rank] is None:
                yield (new_file, new_rank)
    elif piece == 'B':
        for delta in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for step in range(1, 5):
                new_file, new_rank = file + delta[0] * step, rank + delta[1] * step
                if 0 <= new_file < 5 and 0 <= new_rank < 5 and state['board'][piece][new_file, new_rank] is None:
                    yield (new_file, new_rank)
                elif state['board'][piece][new_file, new_rank] is not None:
                    break
    elif piece == 'Q':
        for delta in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for step in range(1, 5):
                new_file, new_rank = file + delta[0] * step, rank + delta[1] * step
                if 0 <= new_file < 5 and 0 <= new_rank < 5 and state['board'][piece][new_file, new_rank] is None:
                    yield (new_file, new_rank)
                elif state['board'][piece][new_file, new_rank] is not None:
                    break
    elif piece == 'K':
        for delta in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            new_file, new_rank = file + delta[0], rank + delta[1]
            if 0 <= new_file < 5 and 0 <= new_rank < 5 and state['board'][piece][new_file, new_rank] is None:
                yield (new_file, new_rank)
    return []

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['turn']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['checkmate']:
        return [-1.0, 1.0]
    elif state['stalemate']:
        return [0.0, 0.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state['checkmate']:
        return []
    elif state['stalemate']:
        return []
    else:
        return get_possible_moves(state)

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {}
    player_1_obs = {}
    for file in 'abcdefgh':
        for rank in range(1, 6):
            obs = state['board'].get(f'{file}{rank}', None)
            if obs is not None:
                player_0_obs[f'{file}{rank}'] = obs
                player_1_obs[f'{file}{rank}'] = obs
    return [player_0_obs, player_1_obs]