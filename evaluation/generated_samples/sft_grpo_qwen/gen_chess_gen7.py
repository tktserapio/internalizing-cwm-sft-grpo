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
    return {
        'board': {
            'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K',
            'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P',
            'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.',
            'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.',
            'a5': 'r', 'b5': 'n', 'c5': 'b', 'd5': 'q', 'e5': 'k'
        },
        'current_player': 0,
        'turn_count': 0,
        'checkmate': False,
        'stalemate': False,
        'en_passant_target': None,
        'promoted_piece': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    piece, from_square, to_square = action.split('_')
    from_square = from_square.lower()
    to_square = to_square.lower()

    # Update the board
    new_state['board'][to_square] = new_state['board'][from_square]
    new_state['board'][from_square] = '.'

    # Handle special rules
    if piece == 'p':
        if to_square == 'e5' and new_state['board']['e4'] == 'P':
            new_state['en_passant_target'] = 'e4'
        elif to_square == 'e2' and new_state['board']['e3'] == 'P':
            new_state['en_passant_target'] = 'e3'
        else:
            new_state['en_passant_target'] = None
    elif piece == 'P':
        if to_square == 'e1' and new_state['board']['e2'] == 'P':
            new_state['promoted_piece'] = 'Q'
        elif to_square == 'e1' and new_state['board']['e2'] == 'R':
            new_state['promoted_piece'] = 'R'
        elif to_square == 'e1' and new_state['board']['e2'] == 'B':
            new_state['promoted_piece'] = 'B'
        elif to_square == 'e1' and new_state['board']['e2'] == 'N':
            new_state['promoted_piece'] = 'N'
        else:
            new_state['promoted_piece'] = None

    # Update the current player
    new_state['current_player'] = 1 - new_state['current_player']
    new_state['turn_count'] += 1

    # Handle en passant
    if new_state['en_passant_target']:
        captured_piece = new_state['board'][new_state['en_passant_target']]
        del new_state['board'][new_state['en_passant_target']]
        new_state['board'][to_square] = captured_piece
        new_state['en_passant_target'] = None

    # Handle promotion
    if new_state['promoted_piece']:
        new_state['board'][to_square] = new_state['promoted_piece']
        new_state['promoted_piece'] = None

    # Check for checkmate
    if checkmate(new_state):
        new_state['checkmate'] = True

    return new_state

def checkmate(state: State) -> bool:
    """
    Checks if the current player is in checkmate.
    """
    king_square = find_king_square(state)
    if not king_square:
        return False
    king_row, king_col = king_square
    opponent_moves = get_opponent_moves(state)
    for move in opponent_moves:
        if move == king_square:
            return True
    return False

def find_king_square(state: State) -> tuple[int, int] | None:
    """
    Finds the square of the king for the current player.
    """
    for square, piece in state['board'].items():
        if piece == 'K' and state['current_player'] == 0:
            return square
        elif piece == 'k' and state['current_player'] == 1:
            return square
    return None

def get_opponent_moves(state: State) -> List[tuple[int, int]]:
    """
    Returns all possible moves for the opponent.
    """
    opponent_moves = []
    for square, piece in state['board'].items():
        if piece != '.' and state['current_player'] == 1 - int(piece.isupper()):
            for move in get_possible_moves(square, piece, state):
                opponent_moves.append(move)
    return opponent_moves

def get_possible_moves(square: str, piece: str, state: State) -> List[tuple[int, int]]:
    """
    Returns all possible moves for a given piece and square.
    """
    row, col = parse_square(square)
    moves = []
    if piece == 'P':
        if state['current_player'] == 0:
            if row == 1 and state['board'][f'{col}2'] == '.':
                moves.append((row + 1, col))
            if row == 1 and state['board'][f'{col}2'] == 'P':
                moves.append((row + 1, col))
            if row > 1 and state['board'][f'{col}{row - 1}'] == '.':
                moves.append((row - 1, col))
            if row > 1 and state['board'][f'{col}{row - 1}'] == 'P':
                moves.append((row - 1, col))
            if col > 1 and state['board'][f'{chr(ord(col) - 1)}{row - 1}'] == '.':
                moves.append((row - 1, chr(ord(col) - 1)))
            if col < 5 and state['board'][f'{chr(ord(col) + 1)}{row - 1}'] == '.':
                moves.append((row - 1, chr(ord(col) + 1)))
        else:
            if row == 4 and state['board'][f'{col}3'] == '.':
                moves.append((row + 1, col))
            if row == 4 and state['board'][f'{col}3'] == 'P':
                moves.append((row + 1, col))
            if row < 4 and state['board'][f'{col}{row + 1}'] == '.':
                moves.append((row + 1, col))
            if row < 4 and state['board'][f'{col}{row + 1}'] == 'P':
                moves.append((row + 1, col))
            if col > 1 and state['board'][f'{chr(ord(col) - 1)}{row + 1}'] == '.':
                moves.append((row + 1, chr(ord(col) - 1)))
            if col < 5 and state['board'][f'{chr(ord(col) + 1)}{row + 1}'] == '.':
                moves.append((row + 1, chr(ord(col) + 1)))
    elif piece == 'N':
        moves = [(row + 2, col + 1), (row + 2, col - 1), (row - 2, col + 1), (row - 2, col - 1),
                 (row + 1, col + 2), (row + 1, col - 2), (row - 1, col + 2), (row - 1, col - 2)]
    elif piece == 'B':
        moves = [(row + i, col + j) for i in range(1, 5) for j in range(1, 5) if (i == j or i == -j)]
    elif piece == 'R':
        moves = [(row + i, col) for i in range(1, 5) if row + i <= 5] + \
               [(row - i, col) for i in range(1, 5) if row - i >= 1] + \
               [(row, col + i) for i in range(1, 5) if col + i <= 5] + \
               [(row, col - i) for i in range(1, 5) if col - i >= 1]
    elif piece == 'Q':
        moves = [(row + i, col + j) for i in range(1, 5) for j in range(1, 5) if (i == j or i == -j)] + \
               [(row + i, col) for i in range(1, 5) if row + i <= 5] + \
               [(row - i, col) for i in range(1, 5) if row - i >= 1] + \
               [(row, col + i) for i in range(1, 5) if col + i <= 5] + \
               [(row, col - i) for i in range(1, 5) if col - i >= 1]
    elif piece == 'K':
        moves = [(row + i, col + j) for i in range(-1, 2) for j in range(-1, 2) if (i == j or i == -j) and (row + i <= 5 and row + i >= 1) and (col + j <= 5 and col + j >= 1)]
    return moves

def parse_square(square: str) -> tuple[int, int]:
    """
    Parses the square into row and column indices.
    """
    col = ord(square[0]) - ord('a') + 1
    row = 6 - int(square[1])
    return row, col

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['current_player']

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
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state['checkmate']:
        return []
    return get_possible_actions(state)

def get_possible_actions(state: State) -> List[Action]:
    """
    Returns possible actions for the current player.
    """
    legal_actions = []
    for square, piece in state['board'].items():
        if piece != '.' and state['current_player'] == 1 - int(piece.isupper()):
            for move in get_possible_moves(square, piece, state):
                legal_actions.append(f"{piece}_{square}_{move}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {
        'board': {k: v for k, v in state['board'].items() if k[0] != 'e'},
        'current_player': state['current_player'],
        'turn_count': state['turn_count'],
        'checkmate': state['checkmate'],
        'stalemate': state['stalemate'],
        'en_passant_target': state['en_passant_target'],
        'promoted_piece': state['promoted_piece']
    }
    player_1_obs = {
        'board': {k: v for k, v in state['board'].items() if k[0] == 'e'},
        'current_player': state['current_player'],
        'turn_count': state['turn_count'],
        'checkmate': state['checkmate'],
        'stalemate': state['stalemate'],
        'en_passant_target': state['en_passant_target'],
        'promoted_piece': state['promoted_piece']
    }
    return [player_0_obs, player_1_obs]