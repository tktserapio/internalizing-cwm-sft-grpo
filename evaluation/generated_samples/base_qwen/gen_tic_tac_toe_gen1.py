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

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initialize the board as a 6x6 numpy array filled with zeros
    board = np.zeros((6, 6))
    return {
        'board': board.tolist(),
        'current_player': 0,
        'winner': None,
        'game_over': False
    }

# Function to apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    # Convert the action string into a tuple (row, col)
    row, col = map(int, action.split(','))
    
    # Check if the action is valid
    if state['board'][row][col] != 0:
        raise ValueError("Invalid action: Cell already occupied.")
    
    # Update the board with the current player's mark
    state['board'][row][col] = state['current_player'] + 1
    
    # Switch the current player
    state['current_player'] = 1 - state['current_player']
    
    # Check for a win condition
    check_winner(state)
    
    # Check if the game is over
    if state['winner'] is None and np.all(state['board'] != 0):
        state['game_over'] = True
    
    return state

# Function to check if there's a winner
def check_winner(state: State):
    board = state['board']
    n = 6
    
    # Check horizontal lines
    for i in range(n):
        for j in range(n - 3):
            if board[i][j] == board[i][j+1] == board[i][j+2] == board[i][j+3] and board[i][j] != 0:
                state['winner'] = state['current_player'] + 1
                return
    
    # Check vertical lines
    for j in range(n):
        for i in range(n - 3):
            if board[i][j] == board[i+1][j] == board[i+2][j] == board[i+3][j] and board[i][j] != 0:
                state['winner'] = state['current_player'] + 1
                return
    
    # Check diagonal lines (top-left to bottom-right)
    for i in range(n - 3):
        for j in range(n - 3):
            if board[i][j] == board[i+1][j+1] == board[i+2][j+2] == board[i+3][j+3] and board[i][j] != 0:
                state['winner'] = state['current_player'] + 1
                return
    
    # Check diagonal lines (bottom-left to top-right)
    for i in range(3, n):
        for j in range(n - 3):
            if board[i][j] == board[i-1][j+1] == board[i-2][j+2] == board[i-3][j+3] and board[i][j] != 0:
                state['winner'] = state['current_player'] + 1
                return

# Function to get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Player {}'.format(player_id + 1)

# Function to get the rewards per player
def get_rewards(state: State) -> list[float]:
    if state['winner'] is None:
        return [0.0, 0.0]
    else:
        return [1.0, 0.0] if state['winner'] == 1 else [0.0, 1.0]

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    board = state['board']
    n = 6
    current_player = state['current_player']
    legal_actions = []
    
    for i in range(n):
        for j in range(n):
            if board[i][j] == 0:
                legal_actions.append(f"{i},{j}")
    
    return legal_actions

# Function to get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    board = state['board']
    n = 6
    observations = []
    
    for i in range(n):
        for j in range(n):
            if board[i][j] == 0:
                observations.append({
                    'board': board.tolist(),
                    'current_player': state['current_player'],
                    'legal_actions': get_legal_actions(state),
                    'winner': state['winner']
                })
            else:
                observations.append({
                    'board': board.tolist(),
                    'current_player': state['current_player'],
                    'legal_actions': [],
                    'winner': state['winner']
                })
    
    return observations