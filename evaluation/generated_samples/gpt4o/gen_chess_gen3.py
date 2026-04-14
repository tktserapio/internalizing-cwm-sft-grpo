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

# Constants for players
WHITE = 0
BLACK = 1

# Initial board setup
INITIAL_BOARD = [
    ['r', 'n', 'b', 'q', 'k'],
    ['p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K']
]

# Helper function to create a deep copy of the board
def copy_board(board: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in board]

# Function to get the initial state of the game
def get_initial_state() -> State:
    return {
        'board': copy_board(INITIAL_BOARD),
        'current_player': WHITE,
        'move_count': 0,
        'terminal': False,
        'winner': None
    }

# Function to get the current player
def get_current_player(state: State) -> int:
    if state['terminal']:
        return -4
    return state['current_player']

# Function to get the player name
def get_player_name(player_id: int) -> str:
    return "White" if player_id == WHITE else "Black"

# Function to get rewards
def get_rewards(state: State) -> List[float]:
    if not state['terminal']:
        return [0.0, 0.0]
    if state['winner'] == WHITE:
        return [1.0, -1.0]
    elif state['winner'] == BLACK:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]  # Draw

# Function to get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state['terminal']:
        return []
    # This function should generate all legal moves for the current player
    # For simplicity, this is a placeholder and should be implemented with full move generation logic
    return []

# Function to apply an action and return the new state
def apply_action(state: State, action: Action) -> State:
    new_state = {
        'board': copy_board(state['board']),
        'current_player': 1 - state['current_player'],
        'move_count': state['move_count'] + 1,
        'terminal': False,
        'winner': None
    }
    # Parse the action and update the board
    # This is a placeholder for the actual move application logic
    # Update the terminal state and winner if necessary
    return new_state

# Function to get observations for both players
def get_observations(state: State) -> List[PlayerObservation]:
    return [state, state]  # Perfect information game

# Additional helper functions for move generation, checking for check/checkmate, etc., would be needed
# to fully implement the game's logic.