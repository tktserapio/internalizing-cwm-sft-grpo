import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Required Functions
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
    new_state = copy.deepcopy(state)
    piece, from_square, to_square = action.split('_')
    from_square = from_square.lower()
    to_square = to_square.lower()

    # Get the current player
    current_player = get_current_player(new_state)
    
    # Check if the action is valid
    if not new_state['board'].get(from_square):
        raise ValueError(f"Invalid move: No piece at {from_square}")
    
    if not new_state['board'].get(to_square):
        if piece == 'p':
            # Pawn promotion
            new_state['board'][to_square] = piece.upper()
        else:
            new_state['board'][to_square] = piece
            new_state['board'].pop(from_square)
    else:
        raise ValueError(f"Invalid move: Target square {to_square} already occupied")
    
    # Update the board
    new_state['board'][to_square] = piece
    new_state['board'].pop(from_square)
    
    # Update the current player
    new_state['current_player'] = (current_player + 1) % 2
    
    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state.get('current_player', -4)

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return ['Player 0', 'Player 1'][player_id]

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # Determine the winner based on the game rules
    winner = determine_winner(state)
    if winner == 0:
        return [1.0, -1.0]
    elif winner == 1:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def determine_winner(state: State) -> int:
    """
    Determines the winner based on the game rules.
    """
    # Check for stalemate
    if not get_legal_actions(state):
        return 2  # Stalemate

    # Check for 50-move rule
    if is_five_zero_move_rule(state):
        return 2  # Stalemate

    # Check for insufficient material
    if is_insufficient_material(state):
        return 2  # Stalemate

    # Check for checkmate
    if is_checkmate(state):
        return get_current_player(state)

    return -1  # Game continues

def is_five_zero_move_rule(state: State) -> bool:
    """
    Checks if the 50-move rule applies.
    """
    # Count the number of moves
    moves_count = 0
    for _ in range(50):
        if get_legal_actions(state):
            moves_count += 1
        state = apply_action(state, get_legal_actions(state)[0])
    return moves_count >= 50

def is_insufficient_material(state: State) -> bool:
    """
    Checks if the game is a draw due to insufficient material.
    """
    # Check if both sides have only pawns and/or knights
    white_pieces = set(piece for piece in state['board'].values() if piece.islower())
    black_pieces = set(piece for piece in state['board'].values() if piece.isupper())
    return len(white_pieces - {'p', 'n'}) == 0 and len(black_pieces - {'p', 'n'}) == 0

def is_checkmate(state: State) -> bool:
    """
    Checks if the game is in checkmate.
    """
    # Check if the current player is in check and has no legal moves
    current_player = get_current_player(state)
    for square, piece in state['board'].items():
        if piece.islower() and piece != 'p' and piece != 'n':
            # Check if the piece can move out of check
            for move in get_legal_actions(state):
                if move.startswith(square):
                    return False
    return True

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    # Implement the logic to generate legal actions
    pass

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Implement the logic to generate observations
    pass