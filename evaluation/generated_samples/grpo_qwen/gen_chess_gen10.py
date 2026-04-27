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
    # Initialize the board with pieces in their starting positions
    board = {
        'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K',
        'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P',
        'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.',
        'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.',
        'a5': 'r', 'b5': 'n', 'c5': 'b', 'd5': 'q', 'e5': 'k'
    }
    return {'board': board}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    board = state['board']
    piece, from_square, to_square = action.split('_')
    from_square = from_square.lower()
    to_square = to_square.lower()

    # Validate the action
    if from_square not in board or to_square not in board:
        raise ValueError("Invalid move: from or to square not found.")
    
    # Get the piece and its current position
    piece_type = board[from_square]
    from_position = (int(from_square[1]) - 1, ord(from_square[0]) - ord('a'))
    to_position = (int(to_square[1]) - 1, ord(to_square[0]) - ord('a'))

    # Perform the move
    board[to_position[0]*5 + to_position[1]] = piece_type
    board[from_position[0]*5 + from_position[1]] = '.'
    
    # Update the state
    new_state = state.copy()
    new_state['board'] = board
    
    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    # Determine the current player based on whose turn it is
    board = state['board']
    white_pawns = sum(1 for square in board.values() if square == 'P' and ord(square[0]) < 97)
    black_pawns = sum(1 for square in board.values() if square == 'p' and ord(square[0]) >= 97)
    
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
    return ['Player 0', 'Player 1'][player_id]

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    current_player = get_current_player(state)
    if current_player == -4:
        return [0.0, 0.0]  # Terminal state
    else:
        return [0.0, 0.0]  # Non-terminal state

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    board = state['board']
    legal_actions = []
    
    for square, piece in board.items():
        if piece != '.':
            # Pawn movement
            if piece == 'P':
                if square[0] == '2':  # White pawn moves from start
                    for i in range(-1, 2):
                        if board.get(f'{square[0]}{chr(ord(square[0]) + i)}{square[1]}') == '.':
                            legal_actions.append(f"P_{square}_{chr(ord(square[0]) + i)}{square[1]}")
                else:  # Normal pawn move
                    for i in range(-1, 2):
                        if board.get(f'{square[0]}{chr(ord(square[0]) + i)}{square[1]}') in ('.', 'P'):
                            legal_actions.append(f"P_{square}_{chr(ord(square[0]) + i)}{square[1]}")
            elif piece == 'p':
                for i in range(-1, 2):
                    if board.get(f'{square[0]}{chr(ord(square[0]) + i)}{square[1]}') in ('.', 'p'):
                        legal_actions.append(f"p_{square}_{chr(ord(square[0]) + i)}{square[1]}")
            
            # Promotion
            if piece in ('P', 'p') and square[0] == '5':
                for piece_type in ('Q', 'R', 'B', 'N'):
                    legal_actions.append(f"{piece}_{square}_Q")
                    legal_actions.append(f"{piece}_{square}_R")
                    legal_actions.append(f"{piece}_{square}_B")
                    legal_actions.append(f"{piece}_{square}_N")
            
            # Other piece movements
            if piece in ('R', 'N', 'B', 'Q', 'K'):
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if abs(i) + abs(j) == 1:  # Knight move
                            if board.get(f'{square[0]}{chr(ord(square[0]) + i)}{square[1]}') in ('.', 'P'):
                                legal_actions.append(f"{piece}_{square}_{chr(ord(square[0]) + i)}{square[1]}")
                        elif abs(i) + abs(j) > 1:  # Rook, Bishop, or Queen move
                            for k in range(1, 5):
                                next_square = f'{square[0]}{chr(ord(square[0]) + i*k)}{square[1]}'
                                if board.get(next_square) in ('.', 'P'):
                                    legal_actions.append(f"{piece}_{square}_{next_square}")
                                else:
                                    break
            
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    observations = []
    
    for player_id in range(2):
        observation = {}
        for square, piece in board.items():
            if piece != '.':
                file = square[0]
                rank = square[1]
                observation[f"{file}{rank}"] = piece
        observations.append(observation)
    
    return observations