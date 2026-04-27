import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Constants
BOARD_SIZE = 5
WHITE_START_RANKS = [1, 2]
BLACK_START_RANKS = [4, 5]
PAWN_START_RANK = 2
PAWN_START_FILE = 'e'
PAWN_PROMOTION_RANK = 0
PAWN_PROMOTION_FILES = ['a', 'b', 'c', 'd', 'e']

# Helper function to convert file and rank to coordinates
def file_rank_to_coords(file, rank):
    return rank - 1, ord(file) - ord('a')

# Helper function to convert coordinates to file and rank
def coords_to_file_rank(coords):
    rank = coords[0] + 1
    file = chr(coords[1] + ord('a'))
    return file, rank

# Helper function to check if a move is valid
def is_valid_move(action, state):
    # Extract pieces and target
    piece, from_coords, to_coords = action.split('_')
    from_coords = tuple(map(int, from_coords))
    to_coords = tuple(map(int, to_coords))

    # Check if the move is within the board
    if not (0 <= from_coords[0] < BOARD_SIZE and 0 <= from_coords[1] < BOARD_SIZE and
            0 <= to_coords[0] < BOARD_SIZE and 0 <= to_coords[1] < BOARD_SIZE):
        return False

    # Check if the piece belongs to the current player
    if state['board'][from_coords] != 'K' and state['board'][from_coords] != 'Q' and \
       state['board'][from_coords] != 'R' and state['board'][from_coords] != 'B' and \
       state['board'][from_coords] != 'N' and state['board'][from_coords] != 'P':
        return False

    # Check if the move is a legal move for the given piece
    if piece == 'P':
        return is_pawn_move(from_coords, to_coords, state)
    elif piece == 'K':
        return is_king_move(from_coords, to_coords, state)
    elif piece == 'Q':
        return is_queen_move(from_coords, to_coords, state)
    elif piece == 'R':
        return is_rook_move(from_coords, to_coords, state)
    elif piece == 'B':
        return is_bishop_move(from_coords, to_coords, state)
    elif piece == 'N':
        return is_knight_move(from_coords, to_coords, state)
    else:
        raise ValueError("Invalid piece")

# Helper function to check if a pawn move is valid
def is_pawn_move(from_coords, to_coords, state):
    # Check if the pawn is moving forward
    if abs(to_coords[0] - from_coords[0]) != 1:
        return False
    # Check if the pawn is capturing
    if abs(to_coords[1] - from_coords[1]) != 1:
        return False
    # Check if the pawn is moving from its starting rank
    if state['board'][from_coords] == 'P' and to_coords[0] == PAWN_START_RANK and to_coords[1] == PAWN_START_FILE:
        return True
    # Check if the pawn is moving forward from its normal rank
    if state['board'][from_coords] == 'P' and to_coords[0] == PAWN_START_RANK + 1 and to_coords[1] == PAWN_START_FILE:
        return True
    # Check if the pawn is capturing
    if state['board'][from_coords] == 'P' and abs(to_coords[1] - from_coords[1]) == 1 and \
       state['board'][tuple(map(lambda x: x + 1, to_coords))] != '.':
        return True
    return False

# Helper function to check if a king move is valid
def is_king_move(from_coords, to_coords, state):
    # Check if the king is moving one square in any direction
    if abs(to_coords[0] - from_coords[0]) > 1 or abs(to_coords[1] - from_coords[1]) > 1:
        return False
    return True

# Helper function to check if a queen move is valid
def is_queen_move(from_coords, to_coords, state):
    # Check if the queen is moving horizontally, vertically, or diagonally
    if abs(to_coords[0] - from_coords[0]) == abs(to_coords[1] - from_coords[1]):
        return True
    return False

# Helper function to check if a rook move is valid
def is_rook_move(from_coords, to_coords, state):
    # Check if the rook is moving horizontally or vertically
    if to_coords[0] == from_coords[0] or to_coords[1] == from_coords[1]:
        return True
    return False

# Helper function to check if a bishop move is valid
def is_bishop_move(from_coords, to_coords, state):
    # Check if the bishop is moving diagonally
    if abs(to_coords[0] - from_coords[0]) == abs(to_coords[1] - from_coords[1]):
        return True
    return False

# Helper function to check if a knight move is valid
def is_knight_move(from_coords, to_coords, state):
    # Check if the knight is moving in an L-shape
    if abs(to_coords[0] - from_coords[0]) == 2 and abs(to_coords[1] - from_coords[1]) == 1:
        return True
    if abs(to_coords[0] - from_coords[0]) == 1 and abs(to_coords[1] - from_coords[1]) == 2:
        return True
    return False

# Helper function to get the current player
def get_current_player(state):
    if state['turn'] % 2 == 0:
        return 0
    else:
        return 1

# Helper function to get the name of the player
def get_player_name(player_id):
    if player_id == 0:
        return 'White'
    else:
        return 'Black'

# Helper function to get the rewards
def get_rewards(state):
    if state['winner'] == -4:
        return [1.0, -1.0]
    else:
        return [0.0, 0.0]

# Helper function to check if the game is terminal
def is_terminal_state(state):
    if state['winner'] != -4:
        return False
    return True

# Helper function to get the legal actions
def get_legal_actions(state):
    legal_actions = []
    for rank in range(BOARD_SIZE):
        for file in 'abcdefgh':
            coords = file_rank_to_coords(file, rank)
            piece = state['board'][coords]
            if piece != '.':
                if piece == 'K':
                    for next_rank in range(BOARD_SIZE):
                        for next_file in 'abcdefgh':
                            next_coords = file_rank_to_coords(next_file, next_rank)
                            if is_valid_move(f'{piece}_{coords[0]}_{next_coords[0]}_{next_coords[1]}', state):
                                legal_actions.append(f'{piece}_{coords[0]}_{next_coords[0]}_{next_coords[1]}')
                else:
                    for next_rank in range(rank + 1, BOARD_SIZE):
                        for next_file in 'abcdefgh':
                            next_coords = file_rank_to_coords(next_file, next_rank)
                            if is_valid_move(f'{piece}_{coords[0]}_{next_coords[0]}_{next_coords[1]}', state):
                                legal_actions.append(f'{piece}_{coords[0]}_{next_coords[0]}_{next_coords[1]}')
                    for prev_rank in range(rank - 1, -1, -1):
                        for prev_file in 'abcdefgh':
                            prev_coords = file_rank_to_coords(prev_file, prev_rank)
                            if is_valid_move(f'{piece}_{coords[0]}_{prev_coords[0]}_{prev_coords[1]}', state):
                                legal_actions.append(f'{piece}_{coords[0]}_{prev_coords[0]}_{prev_coords[1]}')
                    for next_file in 'abcdefgh':
                        next_coords = file_rank_to_coords(next_file, rank + 1)
                        if is_valid_move(f'{piece}_{coords[0]}_{next_coords[0]}_{next_coords[1]}', state):
                            legal_actions.append(f'{piece}_{coords[0]}_{next_coords[0]}_{next_coords[1]}')
                    for prev_file in 'abcdefgh':
                        prev_coords = file_rank_to_coords(prev_file, rank - 1)
                        if is_valid_move(f'{piece}_{coords[0]}_{prev_coords[0]}_{prev_coords[1]}', state):
                            legal_actions.append(f'{piece}_{coords[0]}_{prev_coords[0]}_{prev_coords[1]}')
                    if piece == 'P':
                        if rank == PAWN_START_RANK and to_coords[1] in PAWN_PROMOTION_FILES:
                            legal_actions.append(f'{piece}_{coords[0]}_{to_coords[0]}_{to_coords[1]}_Q')
                            legal_actions.append(f'{piece}_{coords[0]}_{to_coords[0]}_{to_coords[1]}_R')
                            legal_actions.append(f'{piece}_{coords[0]}_{to_coords[0]}_{to_coords[1]}_B')
                            legal_actions.append(f'{piece}_{coords[0]}_{to_coords[0]}_{to_coords[1]}_N')
    return legal_actions

# Helper function to get the observations
def get_observations(state):
    obs_0 = {'board': state['board'], 'turn': state['turn']}
    obs_1 = {'board': state['board'], 'turn': state['turn']}
    return [obs_0, obs_1]

# Helper function to get the initial state
def get_initial_state():
    board = {}
    for rank in range(BOARD_SIZE):
        for file in 'abcdefgh':
            coords = file_rank_to_coords(file, rank)
            if rank in WHITE_START_RANKS:
                board[coords] = 'K'
            elif rank in BLACK_START_RANKS:
                board[coords] = 'k'
            else:
                board[coords] = '.'
    state = {
        'board': board,
        'turn': 0,
        'winner': -4
    }
    return state

# Helper function to apply an action
def apply_action(state, action):
    new_state = copy.deepcopy(state)
    piece, from_coords, to_coords = action.split('_')
    from_coords = tuple(map(int, from_coords))
    to_coords = tuple(map(int, to_coords))
    
    # Update the board
    new_state['board'][from_coords] = '.'
    new_state['board'][to_coords] = piece
    
    # Update the turn
    new_state['turn'] += 1
    
    # Check for checkmate
    if is_checkmate(new_state):
        new_state['winner'] = get_current_player(new_state)
    
    return new_state

# Helper function to check for checkmate
def is_checkmate(state):
    king_coords = None
    for rank in range(BOARD_SIZE):
        for file in 'abcdefgh':
            coords = file_rank_to_coords(file, rank)
            if state['board'][coords] == 'K':
                king_coords = coords
                break
        if king_coords:
            break
    
    if not king_coords:
        return False
    
    for rank in range(BOARD_SIZE):
        for file in 'abcdefgh':
            coords = file_rank_to_coords(file, rank)
            if state['board'][coords] != '.':
                if is_valid_move(f'{state["board"][coords]}_{coords[0]}_{coords[0]}_{coords[1]}', state):
                    return False
    return True