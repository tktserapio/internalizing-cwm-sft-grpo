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
    # Initialize the board with the given positions
    board = {
        'r': {'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K'},
        'n': {'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K'},
        'b': {'c1': 'B', 'd1': 'Q', 'e1': 'K'},
        'q': {'d1': 'Q', 'e1': 'K'},
        'k': {'e1': 'K'},
        'p': {'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P'},
        'r': {'a5': 'R', 'b5': 'N', 'c5': 'B', 'd5': 'Q', 'e5': 'K'},
        'n': {'b5': 'N', 'c5': 'B', 'd5': 'Q', 'e5': 'K'},
        'b': {'c5': 'B', 'd5': 'Q', 'e5': 'K'},
        'q': {'d5': 'Q', 'e5': 'K'},
        'k': {'e5': 'K'}
    }
    return {'board': board}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Extract the piece, from square, to square from the action string
    piece, from_square, to_square = action.split('_')
    from_square = from_square.lower()
    to_square = to_square.lower()

    # Get the current board state
    board = state['board']

    # Get the piece from the board
    piece_from = board[piece][from_square]

    # Update the board with the new position
    board[piece][from_square] = '.'
    board[piece][to_square] = piece_from

    # Handle pawn promotion
    if piece == 'p' and (to_square == 'e5' or to_square == 'e1'):
        board[piece][to_square] = piece + '_Q'

    # Determine the new state
    new_state = get_initial_state()
    new_state['board'] = board

    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    # Determine the current player based on whose turn it is
    pieces = ['r', 'n', 'b', 'q', 'k', 'p']
    for piece in pieces:
        if piece in state['board']:
            return 0 if piece in state['board']['a1'] else 1
    return -4

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # Determine the winner based on the current state
    winner = get_current_player(state)
    if winner == 0:
        return [1.0, -1.0]
    elif winner == 1:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    # Get the current player
    current_player = get_current_player(state)
    if current_player == -4:
        return []  # Terminal state

    # Get the board state
    board = state['board']
    pieces = ['r', 'n', 'b', 'q', 'k', 'p']
    legal_actions = []

    # Iterate over each piece and its possible moves
    for piece in pieces:
        for square, piece_type in board[piece].items():
            if piece_type != '.':
                for move in get_possible_moves(piece, square, board):
                    action = f"{piece}_{square}_{move}"
                    legal_actions.append(action)

    return legal_actions

def get_possible_moves(piece: str, square: str, board: Dict[str, str]) -> List[str]:
    """
    Returns a list of possible moves for a given piece and square.
    """
    # Define the movement rules for each piece
    movement_rules = {
        'r': [(1, 0), (0, 1), (-1, 0), (0, -1)],
        'n': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
        'b': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
        'q': [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
        'k': [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
        'p': [(1, 0)]
    }

    # Get the possible moves for the given piece and square
    possible_moves = []
    for dx, dy in movement_rules[piece]:
        nx, ny = int(square[0]), int(square[1])
        while 0 <= nx < 5 and 0 <= ny < 5:
            nx += dx
            ny += dy
            if board.get(f'{chr(nx + 97)}{ny + 1}') == '.':
                possible_moves.append(f'{chr(nx + 97)}{ny + 1}')
            elif board.get(f'{chr(nx + 97)}{ny + 1}') != '.' and board[f'{chr(nx + 97)}{ny + 1}'][0] != piece[0]:
                possible_moves.append(f'{chr(nx + 97)}{ny + 1}')
                break
            else:
                break

    return possible_moves

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Get the current player
    current_player = get_current_player(state)
    if current_player == -4:
        return []

    # Get the board state
    board = state['board']
    pieces = ['r', 'n', 'b', 'q', 'k', 'p']
    observations = []

    # Iterate over each piece and its possible moves
    for piece in pieces:
        for square, piece_type in board[piece].items():
            if piece_type != '.':
                observation = {}
                observation['piece'] = piece
                observation['square'] = square
                observation['possible_moves'] = get_possible_moves(piece, square, board)
                observations.append(observation)

    return observations