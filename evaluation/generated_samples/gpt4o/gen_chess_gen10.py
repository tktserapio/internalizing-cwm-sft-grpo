import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants for the game
INITIAL_BOARD = [
    ['r', 'n', 'b', 'q', 'k'],
    ['p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K']
]

PLAYER_NAMES = ["White", "Black"]

# Helper functions
def is_within_bounds(x: int, y: int) -> bool:
    """Check if the position is within the board boundaries."""
    return 0 <= x < 5 and 0 <= y < 5

def get_piece_color(piece: str) -> int:
    """Return 0 for white pieces, 1 for black pieces, and -1 for empty squares."""
    if piece.isupper():
        return 0
    elif piece.islower():
        return 1
    return -1

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [row[:] for row in INITIAL_BOARD],
        'current_player': 0,
        'halfmove_clock': 0,
        'fullmove_number': 1,
        'game_over': False,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        'board': [row[:] for row in state['board']],
        'current_player': state['current_player'],
        'halfmove_clock': state['halfmove_clock'],
        'fullmove_number': state['fullmove_number'],
        'game_over': state['game_over'],
        'winner': state['winner']
    }
    
    # Parse the action
    parts = action.split('_')
    piece, from_square, to_square = parts[0], parts[1], parts[2]
    promotion = parts[3] if len(parts) == 4 else None
    
    from_x, from_y = ord(from_square[0]) - ord('a'), int(from_square[1]) - 1
    to_x, to_y = ord(to_square[0]) - ord('a'), int(to_square[1]) - 1
    
    # Move the piece
    new_state['board'][to_y][to_x] = '.'
    if promotion:
        new_state['board'][to_y][to_x] = promotion.upper() if new_state['current_player'] == 0 else promotion.lower()
    else:
        new_state['board'][to_y][to_x] = piece.upper() if new_state['current_player'] == 0 else piece.lower()
    
    # Update move counters
    new_state['halfmove_clock'] += 1
    if new_state['current_player'] == 1:
        new_state['fullmove_number'] += 1
    
    # Switch players
    new_state['current_player'] = 1 - new_state['current_player']
    
    # Check for game over conditions (checkmate, stalemate, etc.)
    # This is a placeholder; actual implementation would require checking for checkmate/stalemate
    # new_state['game_over'] = check_game_over(new_state)
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state['game_over'] else state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return PLAYER_NAMES[player_id]

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['game_over']:
        if state['winner'] is not None:
            return [1.0, -1.0] if state['winner'] == 0 else [-1.0, 1.0]
        else:
            return [0.0, 0.0]  # Draw
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['game_over']:
        return []
    
    legal_actions = []
    # Generate legal actions based on the current board state and player
    # This is a placeholder; actual implementation would require generating all legal moves
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{'board': state['board'], 'current_player': state['current_player']} for _ in range(2)]

# Note: The above implementation provides a basic structure for the game state management.
# The actual game logic, including move generation and game over checks, would need to be implemented
# for a complete and functional chess engine.