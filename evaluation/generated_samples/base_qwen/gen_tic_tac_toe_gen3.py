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
def parse_action(action_str: Action) -> tuple[int, int]:
    """Parses an action string into a (row, col) tuple."""
    row_col_str = action_str.split(',')
    return (int(row_col_str[0]), int(row_col_str[1]))

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Get the current player
    current_player = state['current_player']
    
    # Parse the action
    row, col = parse_action(action)
    
    # Check if the action is valid
    if state['board'][row][col] != ' ':
        raise ValueError("Invalid action: Cell already occupied.")
    
    # Update the board
    state['board'][row][col] = 'x' if current_player == 0 else 'o'
    
    # Switch the current player
    state['current_player'] = (current_player + 1) % 2
    
    # Check for win condition
    if check_win(state):
        state['winner'] = current_player
        state['game_over'] = True
    
    return state

def check_win(state: State) -> bool:
    """
    Checks if there is a winning line of four marks for the current player.
    """
    board = state['board']
    current_player = state['current_player']
    
    # Check rows and columns
    for i in range(6):
        if (board[i][0] == board[i][1] == board[i][2] == board[i][3] == current_player or
            board[0][i] == board[1][i] == board[2][i] == board[3][i] == current_player):
            return True
    
    # Check diagonals
    if (board[0][0] == board[1][1] == board[2][2] == board[3][3] == current_player or
        board[0][3] == board[1][2] == board[2][1] == board[3][0] == current_player):
        return True
    
    return False

def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    return {
        'board': np.full((6, 6), ' ').tolist(),
        'current_player': 0,
        'winner': None,
        'game_over': False
    }

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Player 1' if player_id == 0 else 'Player 2'

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    if state['game_over']:
        if state['winner'] is None:
            return [0.0, 0.0]  # Draw
        elif state['winner'] == 0:
            return [1.0, -1.0]  # Player 1 wins
        else:
            return [-1.0, 1.0]  # Player 2 wins
    else:
        return [0.0, 0.0]  # Not a terminal state yet

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state['game_over']:
        return []
    
    board = state['board']
    current_player = state['current_player']
    
    legal_actions = []
    for row in range(6):
        for col in range(6):
            if board[row][col] == ' ':
                legal_actions.append(f"{row},{col}")
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    current_player = state['current_player']
    
    player_0_obs = {'board': board, 'legal_actions': get_legal_actions(state)}
    player_1_obs = {'board': board, 'legal_actions': get_legal_actions(state)}
    
    return [player_0_obs, player_1_obs]