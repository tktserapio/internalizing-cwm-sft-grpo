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

def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial board setup
    initial_board = {
        'r': {'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K'},
        'n': {'a2': 'N', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P'},
        'b': {'a3': 'B', 'c3': 'B', 'e3': 'B'},
        'q': {'d1': 'Q'},
        'k': {'e1': 'K'},
        'p': {
            'a2': 'P',
            'b2': 'P',
            'c2': 'P',
            'd2': 'P',
            'e2': 'P',
            'a3': 'P',
            'b3': 'P',
            'c3': 'P',
            'd3': 'P',
            'e3': 'P'
        }
    }
    return {
        'board': initial_board,
        'turn': 0,
        'winner': None,
        'moves': []
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    piece, from_square, to_square = action.split('_')
    from_square = from_square.upper()
    to_square = to_square.upper()

    # Update the board
    new_state['board'][piece][from_square] = '.'
    if piece == 'P':
        new_state['board'][piece][to_square] = 'P'
    else:
        new_state['board'][piece][to_square] = piece

    # Handle promotions
    if piece == 'P' and (to_square == 'E5' or to_square == 'E1'):
        new_state['board'][piece][to_square] += '_Q'

    # Castling is not implemented in this version
    # Handle en passant
    if piece == 'P' and abs(ord(from_square) - ord(to_square)) == 1 and new_state['board']['P'][to_square] == '.':
        new_state['board']['P'][to_square] = 'P'
        new_state['board']['P'][from_square] = '.'
    
    # Handle other piece movements
    if piece == 'K':
        new_state['winner'] = None
    elif piece == 'Q':
        new_state['winner'] = None
    elif piece == 'R':
        new_state['winner'] = None
    elif piece == 'B':
        new_state['winner'] = None
    elif piece == 'N':
        new_state['winner'] = None
    else:
        new_state['winner'] = None

    # Update turn
    new_state['turn'] = (new_state['turn'] + 1) % 2
    new_state['moves'].append(action)

    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['turn']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    winner = state['winner']
    if winner is None:
        return [0.0, 0.0]
    elif winner == 0:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    board = state['board']
    turn = state['turn']
    moves = state['moves']
    winner = state['winner']

    # Check if the game is over
    if winner is not None:
        return []

    # Get the current player's pieces
    if turn == 0:
        player_pieces = ['R', 'N', 'B', 'Q', 'K', 'P']
    else:
        player_pieces = ['r', 'n', 'b', 'q', 'k', 'p']

    # Iterate through each piece and find valid moves
    for piece in player_pieces:
        for square, piece_type in board[piece].items():
            if piece_type != '.':
                # Get possible moves for the piece
                if piece == 'P':
                    possible_moves = get_pawn_moves(board, square, turn)
                elif piece == 'R':
                    possible_moves = get_rook_moves(board, square)
                elif piece == 'N':
                    possible_moves = get_knight_moves(board, square)
                elif piece == 'B':
                    possible_moves = get_bishop_moves(board, square)
                elif piece == 'Q':
                    possible_moves = get_queen_moves(board, square)
                elif piece == 'K':
                    possible_moves = get_king_moves(board, square)
                
                # Filter out moves that would put the king in check
                for move in possible_moves:
                    if not is_in_check(board, move, turn):
                        legal_actions.append(f"{piece}_{square}_{move}")

    return legal_actions

def get_pawn_moves(board, square, turn):
    """
    Returns possible moves for a pawn.
    """
    moves = []
    file = square[0]
    rank = square[1]
    if turn == 0:
        if rank != '1':
            moves.append(f"P_{file}{rank}_P_{file}{rank+1}")
        if rank != '1' and board['P'][f'{file}{rank+1}'] == '.':
            moves.append(f"P_{file}{rank}_P_{file}{rank+2}")
        if file != 'a':
            moves.append(f"P_{file}{rank}_P_{file+1}{rank}")
        if file != 'h':
            moves.append(f"P_{file}{rank}_P_{file-1}{rank}")
    else:
        if rank != '5':
            moves.append(f"P_{file}{rank}_P_{file}{rank-1}")
        if rank != '5' and board['p'][f'{file}{rank-1}'] == '.':
            moves.append(f"P_{file}{rank}_P_{file}{rank-2}")
        if file != 'a':
            moves.append(f"P_{file}{rank}_P_{file+1}{rank}")
        if file != 'h':
            moves.append(f"P_{file}{rank}_P_{file-1}{rank}")
    return moves

def get_rook_moves(board, square):
    """
    Returns possible moves for a rook.
    """
    moves = []
    file = square[0]
    rank = square[1]
    for i in range(1, 5):
        if file != 'a':
            moves.append(f"R_{file}{rank}_{file+str(i)}{rank}")
        if file != 'h':
            moves.append(f"R_{file}{rank}_{file-str(i)}{rank}")
        if rank != '1':
            moves.append(f"R_{file}{rank}_{file}{rank+str(i)}")
        if rank != '5':
            moves.append(f"R_{file}{rank}_{file}{rank-str(i)}")
    return moves

def get_knight_moves(board, square):
    """
    Returns possible moves for a knight.
    """
    moves = []
    file = square[0]
    rank = square[1]
    for i in range(-2, 3):
        for j in range(-2, 3):
            if abs(i) + abs(j) == 3:
                moves.append(f"N_{file}{rank}_{chr(ord(file)+i)}{str(int(rank)+j)}")
    return moves

def get_bishop_moves(board, square):
    """
    Returns possible moves for a bishop.
    """
    moves = []
    file = square[0]
    rank = square[1]
    for i in range(1, 5):
        for j in range(1, 5):
            if file != 'a':
                moves.append(f"B_{file}{rank}_{file+str(i)}{rank+str(j)}")
            if file != 'h':
                moves.append(f"B_{file}{rank}_{file-str(i)}{rank-str(j)}")
    return moves

def get_queen_moves(board, square):
    """
    Returns possible moves for a queen.
    """
    return get_rook_moves(board, square) + get_bishop_moves(board, square)

def get_king_moves(board, square):
    """
    Returns possible moves for a king.
    """
    moves = []
    file = square[0]
    rank = square[1]
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i != 0 or j != 0:
                moves.append(f"K_{file}{rank}_{chr(ord(file)+i)}{str(int(rank)+j)}")
    return moves

def is_in_check(board, move, turn):
    """
    Checks if the move puts the king in check.
    """
    if turn == 0:
        king_square = 'e1'
    else:
        king_square = 'e5'
    new_board = board.copy()
    new_board[move[0]][move[1]] = new_board[king_square]
    new_board[king_square] = '.'
    return is_king_in_check(new_board)

def is_king_in_check(board):
    """
    Checks if the king is in check.
    """
    for piece in ['R', 'N', 'B', 'Q', 'K', 'P']:
        for square, piece_type in board[piece].items():
            if piece_type != '.':
                possible_moves = get_possible_moves(board, square, piece)
                for move in possible_moves:
                    if move == 'K':
                        return True
    return False

def get_possible_moves(board, square, piece):
    """
    Returns possible moves for a given piece.
    """
    moves = []
    file = square[0]
    rank = square[1]
    if piece == 'P':
        moves.extend(get_pawn_moves(board, square, 0))
        moves.extend(get_pawn_moves(board, square, 1))
    elif piece == 'R':
        moves.extend(get_rook_moves(board, square))
    elif piece == 'N':
        moves.extend(get_knight_moves(board, square))
    elif piece == 'B':
        moves.extend(get_bishop_moves(board, square))
    elif piece == 'Q':
        moves.extend(get_queen_moves(board, square))
    elif piece == 'K':
        moves.extend(get_king_moves(board, square))
    return moves

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    observations = []
    board = state['board']
    for player in [0, 1]:
        obs = {}
        for piece in ['R', 'N', 'B', 'Q', 'K', 'P']:
            obs[piece] = {}
            for square, piece_type in board[piece].items():
                if piece_type != '.':
                    obs[piece][square] = piece_type
        obs['turn'] = state['turn']
        obs['winner'] = state['winner']
        obs['moves'] = state['moves']
        observations.append(obs)
    return observations