import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants for the game
WHITE, BLACK = 0, 1
PIECE_SYMBOLS = {'P', 'N', 'B', 'R', 'Q', 'K'}
INITIAL_BOARD = [
    ['r', 'n', 'b', 'q', 'k'],
    ['p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K']
]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [row[:] for row in INITIAL_BOARD],
        'current_player': WHITE,
        'move_count': 0,
        'halfmove_clock': 0,
        'history': []
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        'board': [row[:] for row in state['board']],
        'current_player': 1 - state['current_player'],
        'move_count': state['move_count'] + 1,
        'halfmove_clock': state['halfmove_clock'],
        'history': state['history'] + [action]
    }
    
    # Parse the action
    parts = action.split('_')
    piece, from_square, to_square = parts[0], parts[1], parts[2]
    promotion = parts[3] if len(parts) == 4 else None
    
    from_col, from_row = ord(from_square[0]) - ord('a'), int(from_square[1]) - 1
    to_col, to_row = ord(to_square[0]) - ord('a'), int(to_square[1]) - 1
    
    # Move the piece
    new_state['board'][to_row][to_col] = new_state['board'][from_row][from_col]
    new_state['board'][from_row][from_col] = '.'
    
    # Handle promotion
    if promotion:
        new_state['board'][to_row][to_col] = promotion
    
    # Update halfmove clock
    if piece == 'P' or new_state['board'][to_row][to_col] != '.':
        new_state['halfmove_clock'] = 0
    else:
        new_state['halfmove_clock'] += 1
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if is_terminal(state):
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "White" if player_id == WHITE else "Black"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if is_terminal(state):
        winner = get_winner(state)
        if winner is not None:
            return [1.0, -1.0] if winner == WHITE else [-1.0, 1.0]
        return [0.0, 0.0]  # Draw
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if is_terminal(state):
        return []
    
    legal_actions = []
    # Generate all legal moves for the current player
    # This involves checking each piece and generating valid moves
    # For simplicity, this is a placeholder for move generation logic
    # You would need to implement the actual move generation logic here
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{'board': state['board'], 'current_player': state['current_player']} for _ in range(2)]

def is_terminal(state: State) -> bool:
    """Determines if the current state is terminal."""
    # Check for checkmate, stalemate, or draw conditions
    # Placeholder for actual terminal state logic
    return False

def get_winner(state: State) -> int:
    """Returns the winner of the game, if any."""
    # Determine the winner based on the state
    # Placeholder for actual winner determination logic
    return None

# Note: The actual move generation and checking for check, checkmate, and stalemate
# require additional logic not provided here. This implementation provides a framework
# to build upon for the 5x5 Gardner Minichess game.