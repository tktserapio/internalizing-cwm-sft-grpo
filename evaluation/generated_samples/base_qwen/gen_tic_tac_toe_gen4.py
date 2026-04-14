import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import numpy as np

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def create_board():
    """Create a 6x6 board initialized to None."""
    return np.full((6, 6), None)

def check_winner(board, player):
    """Check if the given player has won the game."""
    # Check rows
    for row in board:
        if all(cell == player for cell in row):
            return True
    # Check columns
    for col in range(6):
        if all(board[row][col] == player for row in range(6)):
            return True
    # Check diagonals
    for i in range(3):  # Only need to check up to 3 because we're looking for 4 in a row
        if all(board[i + j][j] == player for j in range(4)) or \
           all(board[i + 5 - j][j] == player for j in range(4)):
            return True
    return False

def is_draw(board):
    """Check if the game is a draw."""
    return all(cell is not None for row in board for cell in row)

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': create_board(),
        'current_player': 0,
        'winner': None,
        'draw': False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    # Parse action
    row, col = map(int, action.split(','))
    
    # Validate action
    if state['board'][row][col] is not None:
        raise ValueError("Cell already occupied.")
    
    # Apply action
    board = state['board']
    board[row][col] = state['current_player'] + 1  # Mark with player's number
    
    # Switch player
    state['current_player'] = 1 - state['current_player']
    
    # Check for winner
    if check_winner(board, state['current_player'] + 1):
        state['winner'] = state['current_player'] + 1
        state['draw'] = False
    elif is_draw(board):
        state['winner'] = None
        state['draw'] = True
    
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Player {}'.format(player_id + 1)

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['winner'] is not None:
        return [1.0, -1.0] if state['winner'] == 1 else [-1.0, 1.0]
    elif state['draw']:
        return [0.5, 0.5]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['winner'] is not None or state['draw']:
        return []
    else:
        return [f"{row},{col}" for row in range(6) for col in range(6) if state['board'][row][col] is None]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    player_0_obs = {f"row_{i}": [board[i][j] for j in range(6)] for i in range(6)}
    player_1_obs = {f"row_{i}": [board[i][j] for j in range(6)] for i in range(6)}
    return [player_0_obs, player_1_obs]