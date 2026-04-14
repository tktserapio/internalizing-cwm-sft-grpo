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
    file, rank = algebraic_notation[0], algebraic_notation[1]
    file_index = 'abcdefgh'.find(file)
    rank_index = int(rank) - 1
    return (file_index, rank_index)

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial board setup
    board = {
        'r': (4, 0), 'n': (4, 1), 'b': (4, 2), 'q': (4, 3), 'k': (4, 4),
        'p': [(4, i) for i in range(5)],
        'R': (1, 0), 'N': (1, 1), 'B': (1, 2), 'Q': (1, 3), 'K': (1, 4),
        'p': [(1, i) for i in range(5)]
    }
    return {'board': board}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    board = state['board']
    piece, from_coords, to_coords = action.split('_')
    from_coords = algebraic_to_coordinates(from_coords)
    to_coords = algebraic_to_coordinates(to_coords)
    
    # Validate action
    if piece not in board or from_coords not in board[piece] or to_coords not in board:
        raise ValueError("Invalid action")
    
    # Move piece
    piece_type = board[piece][from_coords]
    del board[piece][from_coords]
    board[piece][to_coords] = piece_type
    
    # Handle promotions
    if piece == 'p' and abs(to_coords[1] - from_coords[1]) == 2:
        board[piece][to_coords] = 'Q'
    
    # Castling is not implemented in this version
    # Handle en passant
    if piece == 'p' and to_coords[1] == from_coords[1] + 1 and board[from_coords[1]][from_coords[0]] == 'p':
        del board['p'][algebraic_to_coordinates(f'{from_coords[0]}{from_coords[1]+1}')[1]]
    
    # Handle checkmate/check
    # This is a placeholder for now, actual logic would be complex
    # For simplicity, we assume the game is over after each move
    # In a real implementation, you would need to check for checkmate/check
    # and update the state accordingly
    
    return {'board': board}

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    # Determine the current player based on whose turn it is
    # In this simplified version, we assume the game is always in progress
    return 0

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # In this simplified version, we assume the game is always in progress
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    # Placeholder for legal actions logic
    # In a real implementation, you would need to generate all possible legal moves
    # and filter out those that are not allowed (like moving a piece off the board)
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Placeholder for observation logic
    # In a real implementation, you would need to create observations for each player
    # that reflect their perspective on the board
    return []