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

# Constants for the board setup
INITIAL_BOARD = [
    ['r', 'n', 'b', 'q', 'k'],
    ['p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K']
]

# Helper function to clone the board
def clone_board(board: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in board]

# Function to get the initial state of the game
def get_initial_state() -> State:
    return {
        'board': clone_board(INITIAL_BOARD),
        'current_player': 0,
        'move_count': 0,
        'halfmove_clock': 0,
        'is_terminal': False,
        'winner': None
    }

# Function to get the current player
def get_current_player(state: State) -> int:
    if state['is_terminal']:
        return -4
    return state['current_player']

# Function to get the player name
def get_player_name(player_id: int) -> str:
    return "White" if player_id == 0 else "Black"

# Function to get rewards
def get_rewards(state: State) -> List[float]:
    if not state['is_terminal']:
        return [0.0, 0.0]
    if state['winner'] == 0:
        return [1.0, -1.0]
    elif state['winner'] == 1:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]  # Draw

# Function to apply an action and return the new state
def apply_action(state: State, action: Action) -> State:
    new_state = {
        'board': clone_board(state['board']),
        'current_player': 1 - state['current_player'],
        'move_count': state['move_count'] + 1,
        'halfmove_clock': state['halfmove_clock'],
        'is_terminal': False,
        'winner': None
    }
    
    # Parse the action
    parts = action.split('_')
    piece, from_square, to_square = parts[0], parts[1], parts[2]
    promotion = parts[3] if len(parts) > 3 else None
    
    # Convert algebraic notation to board indices
    from_rank, from_file = 5 - int(from_square[1]), ord(from_square[0]) - ord('a')
    to_rank, to_file = 5 - int(to_square[1]), ord(to_square[0]) - ord('a')
    
    # Move the piece on the board
    new_state['board'][to_rank][to_file] = new_state['board'][from_rank][from_file]
    new_state['board'][from_rank][from_file] = '.'
    
    # Handle promotion
    if promotion:
        new_state['board'][to_rank][to_file] = promotion.lower() if state['current_player'] == 0 else promotion.upper()
    
    # Update halfmove clock
    if piece.upper() == 'P' or new_state['board'][to_rank][to_file] != '.':
        new_state['halfmove_clock'] = 0
    else:
        new_state['halfmove_clock'] += 1
    
    # Check for terminal state (checkmate, stalemate, 50-move rule)
    # This requires additional logic to determine if the game is over
    # For simplicity, assume no terminal state logic is implemented yet
    
    return new_state

# Function to get legal actions
def get_legal_actions(state: State) -> List[Action]:
    if state['is_terminal']:
        return []
    
    # Placeholder for legal actions generation
    # This requires implementing move generation logic for each piece type
    legal_actions = []
    
    # Implement move generation logic here
    
    return legal_actions

# Function to get observations
def get_observations(state: State) -> List[PlayerObservation]:
    return [{'board': state['board'], 'current_player': state['current_player']} for _ in range(2)]

# Note: The above implementation is a skeleton and does not include the full logic for move generation,
# checkmate detection, or other advanced chess rules. These would need to be implemented to have a fully
# functional game engine.