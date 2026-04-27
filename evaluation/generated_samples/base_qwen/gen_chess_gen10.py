import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to convert algebraic notation to coordinates
def algebraic_to_coordinates(algebraic_notation):
    file = algebraic_notation[0]
    rank = 6 - int(algebraic_notation[1])  # Inverting ranks as our convention is 1-5
    return file, rank

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    initial_board = {
        'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K',
        'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P',
        'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.',
        'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.',
        'a5': 'r', 'b5': 'n', 'c5': 'b', 'd5': 'q', 'e5': 'k'
    }
    return {'board': initial_board}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    piece, from_square, to_square = action.split('_')
    from_file, from_rank = algebraic_to_coordinates(from_square)
    to_file, to_rank = algebraic_to_coordinates(to_square)
    
    # Update the board with the new piece location
    new_state['board'][f'{to_file}{to_rank}'] = new_state['board'].pop(f'{from_file}{from_rank}')
    
    # Handle special cases like pawn promotion
    if piece == 'P' and abs(int(to_rank) - int(from_rank)) == 2:
        new_state['board'][f'{to_file}{to_rank}'] = 'Q'
    
    # Handle castling
    if piece == 'K':
        # Castling logic here
        pass
    
    # Handle en passant
    if piece == 'P' and abs(int(to_rank) - int(from_rank)) == 1 and from_square[1] != to_square[1]:
        captured_piece = new_state['board'].pop(f'{to_file}{int(to_rank)-1}')
        new_state['board'][f'{to_file}{int(to_rank)}'] = captured_piece
    
    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    board = state['board']
    white_pawns = sum(1 for square in board.values() if square == 'P' and square.islower())
    black_pawns = sum(1 for square in board.values() if square == 'P' and square.isupper())
    
    if white_pawns > black_pawns:
        return 0
    elif black_pawns > white_pawns:
        return 1
    else:
        return -4  # Terminal state

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return {0: 'White', 1: 'Black'}[player_id]

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    winner = get_current_player(state)
    if winner != -4:
        return [1.0, -1.0] if winner == 0 else [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    board = state['board']
    legal_actions = []
    
    def is_valid_move(piece, from_square, to_square):
        from_file, from_rank = algebraic_to_coordinates(from_square)
        to_file, to_rank = algebraic_to_coordinates(to_square)
        
        if piece == 'P':
            if board[from_square] == 'P' and from_rank == 2:
                # Two-step move
                if board[f'{from_file}{int(from_rank)+1}'] == '.' and board[f'{from_file}{int(from_rank)+2}'] == '.':
                    legal_actions.append(f"P_{from_square}_{f'{to_file}{int(to_rank)+1}_2}")
            else:
                if board[f'{from_file}{int(from_rank)+1}'] == '.':
                    legal_actions.append(f"P_{from_square}_{f'{to_file}{int(to_rank)+1}'}")
        elif piece == 'N':
            if abs(int(to_rank) - int(from_rank)) == 2 and abs(ord(to_file) - ord(from_file)) == 1:
                legal_actions.append(f"N_{from_square}_{to_square}")
        elif piece == 'B':
            if abs(int(to_rank) - int(from_rank)) == abs(ord(to_file) - ord(from_file)):
                legal_actions.append(f"B_{from_square}_{to_square}")
        elif piece == 'R':
            if abs(int(to_rank) - int(from_rank)) == 0 or abs(ord(to_file) - ord(from_file)) == 0:
                legal_actions.append(f"R_{from_square}_{to_square}")
        elif piece == 'Q':
            if abs(int(to_rank) - int(from_rank)) == 0 or abs(ord(to_file) - ord(from_file)) == 0:
                legal_actions.append(f"Q_{from_square}_{to_square}")
        elif piece == 'K':
            if abs(int(to_rank) - int(from_rank)) <= 1 and abs(ord(to_file) - ord(from_file)) <= 1:
                legal_actions.append(f"K_{from_square}_{to_square}")
        elif piece == 'p':
            if board[from_square] == 'p' and from_rank == 4:
                # Two-step move
                if board[f'{from_file}{int(from_rank)-1}'] == '.' and board[f'{from_file}{int(from_rank)-2}'] == '.':
                    legal_actions.append(f"p_{from_square}_{f'{to_file}{int(to_rank)-1}_2}")
            else:
                if board[f'{from_file}{int(from_rank)-1}'] == '.':
                    legal_actions.append(f"p_{from_square}_{f'{to_file}{int(to_rank)-1}'}")
        return legal_actions
    
    for square, piece in board.items():
        if piece.islower():  # White pieces
            for to_square in board.keys():
                if board[to_square] == '.' and is_valid_move(piece, square, to_square):
                    legal_actions.append(f"{piece}_{square}_{to_square}")
        else:  # Black pieces
            for to_square in board.keys():
                if board[to_square] == '.' and is_valid_move(piece, square, to_square):
                    legal_actions.append(f"{piece}_{square}_{to_square}")
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    player_0_obs = {}
    player_1_obs = {}
    
    for square, piece in board.items():
        if piece.islower():
            player_0_obs[square] = piece
        else:
            player_1_obs[square] = piece
    
    return [player_0_obs, player_1_obs]