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
        'board': [
            ['r', 'n', 'b', 'q', 'k'],
            ['p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K']
        ],
        'turn': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Parse the action
    piece, from_square, to_square = action.split('_')
    from_row, from_col = from_square[1], from_square[0]
    to_row, to_col = to_square[1], to_square[0]
    
    # Convert file and rank to index
    from_index = (ord(from_col) - ord('a')) + 5 * (int(from_row) - 1)
    to_index = (ord(to_col) - ord('a')) + 5 * (int(to_row) - 1)
    
    # Get the current piece at the from_square
    current_piece = state['board'][int(from_row) - 1][ord(from_col) - ord('a')]
    
    # Update the board
    state['board'][int(from_row) - 1][ord(from_col) - ord('a')] = '.'
    state['board'][int(to_row) - 1][ord(to_col) - ord('a')] = current_piece
    
    # Handle special cases like promotion, castling, en passant, etc.
    if piece == 'P' and abs(int(from_row) - int(to_row)) == 2:
        # En passant
        pass
    elif piece == 'P' and to_row == 1 or to_row == 5:
        # Promotion
        pass
    elif piece == 'K':
        # Castling
        pass
    
    # Update the turn
    state['turn'] = 1 - state['turn']
    
    return state

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
    else:
        return [1.0 if winner == 0 else -1.0, 1.0 if winner == 1 else -1.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    # Implement logic to generate legal actions based on the current state
    # This is a placeholder implementation
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Implement logic to generate observations based on the current state
    # This is a placeholder implementation
    return []