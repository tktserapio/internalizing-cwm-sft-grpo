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

# Helper function to create an initial state
def get_initial_state():
    # Create an empty 6x6 board
    board = np.full((6, 6), '')
    return {'board': board, 'current_player': 0}

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action string to row, col
    row, col = map(int, action.split(','))
    
    # Check if the action is valid
    if state['board'][row][col] != '':
        raise ValueError("Invalid action: Cell already occupied.")
    
    # Apply the action to the board
    state['board'][row][col] = 'x' if state['current_player'] == 0 else 'o'
    
    # Switch the current player
    state['current_player'] = 1 - state['current_player']
    
    return state

# Function to determine the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Player 1' if player_id == 0 else 'Player 2'

# Function to get the rewards for the current state
def get_rewards(state: State) -> list[float]:
    # Check if the game is over
    if is_game_over(state):
        # If the game is over, check for a win
        if is_winner('x', state):
            return [1.0, -1.0]
        elif is_winner('o', state):
            return [-1.0, 1.0]
        else:
            return [0.0, 0.0]
    else:
        # If the game is not over, it's a draw
        return [0.0, 0.0]

# Function to check if the game is over
def is_game_over(state: State) -> bool:
    # Check rows and columns
    for i in range(6):
        if is_winner(state['board'][i], state['current_player']):
            return True
        if is_winner(state['board'].T[i], state['current_player']):
            return True
    
    # Check diagonals
    for i in range(3):
        if is_winner(np.diag(state['board'], k=i), state['current_player']):
            return True
        if is_winner(np.diag(np.fliplr(state['board']), k=i), state['current_player']):
            return True
    
    # Check if the board is full
    return np.all(state['board'] != '')
    
# Function to check if a player has won
def is_winner(mark: str, player_id: int) -> bool:
    # Check rows and columns
    for i in range(6):
        if all(state['board'][i][j] == mark for j in range(6)) or \
           all(state['board'][j][i] == mark for j in range(6)):
            return True
    
    # Check diagonals
    for i in range(3):
        if all(state['board'][i + k][i + k] == mark for k in range(3)) or \
           all(state['board'][i + k][5 - i + k] == mark for k in range(3)):
            return True
    
    return False

# Function to get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    # Get the current player's marks
    player_marks = state['board'][state['current_player']]
    
    # Find empty cells
    empty_cells = [(r, c) for r in range(6) for c in range(6) if player_marks[r][c] == '']
    
    # Format the actions
    return ['{},{}'.format(r, c) for r, c in empty_cells]

# Function to get observations for the current state
def get_observations(state: State) -> list[PlayerObservation]:
    # Get the current player's marks
    player_marks = state['board'][state['current_player']]
    
    # Create observations
    obs_0 = {'marks': player_marks}
    obs_1 = {'marks': np.flipud(np.rot90(player_marks, 2))}
    
    return [obs_0, obs_1]