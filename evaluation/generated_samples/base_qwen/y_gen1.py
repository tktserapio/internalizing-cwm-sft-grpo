import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to convert coordinates to action string
def coord_to_action(coord: Tuple[int, int]) -> Action:
    return f"{coord[0]},{coord[1]}"

# Initial state setup
def get_initial_state() -> State:
    # Size-4 board for simplicity
    board_size = 4
    initial_state = {
        'board': [
            ['-', '-', '-', '-'],
            ['-', '-', '-', '-'],
            ['-', '-', '-', '-'],
            ['-', '-', '-', '-']
        ],
        'current_player': 0,
        'winner': -4
    }
    return initial_state

# Apply action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action string to coordinates
    x, y = map(int, action.split(','))

    # Check if the action is valid
    if x < 0 or x >= state['board'][0][0]:  # Assuming board is square for simplicity
        raise ValueError("Invalid action")
    
    # Update the board
    board = state['board']
    board[y][x] = 'B' if state['current_player'] == 0 else 'W'
    state['board'] = board
    
    # Switch the current player
    state['current_player'] = (state['current_player'] + 1) % 2
    
    # Check for win condition
    check_winner(board)
    
    return state

# Check for win condition
def check_winner(board: List[List[str]]) -> None:
    # Check rows, columns, and diagonals for a complete line of the current player's stones
    for i in range(len(board)):
        if board[i][i] == board[i][i+1] == board[i][i+2] == board[i][i+3] != '-':
            state['winner'] = 0 if board[i][i] == 'B' else 1
            return
        
        if board[i][0] == board[i][1] == board[i][2] == board[i][3] != '-':
            state['winner'] = 0 if board[i][0] == 'B' else 1
            return
        
    for j in range(4):
        if board[0][j] == board[1][j] == board[2][j] == board[3][j] != '-':
            state['winner'] = 0 if board[0][j] == 'B' else 1
            return
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] == board[3][3] != '-':
        state['winner'] = 0 if board[0][0] == 'B' else 1
        return
    
    if board[0][3] == board[1][2] == board[2][1] == board[3][0] != '-':
        state['winner'] = 0 if board[0][3] == 'B' else 1
        return
    
    # If no winner, continue the game
    if '-' not in ''.join([''.join(row) for row in board]):
        state['winner'] = -4

# Get current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get player name
def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

# Get rewards
def get_rewards(state: State) -> List[float]:
    if state['winner'] == 0:
        return [1.0, 0.0]
    elif state['winner'] == 1:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    board = state['board']
    legal_actions = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == '-':
                legal_actions.append(coord_to_action((i, j)))
    return legal_actions

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    board = state['board']
    player_0_obs = {}
    player_1_obs = {}
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 'B':
                player_0_obs[f"{i},{j}"] = 1
            elif board[i][j] == 'W':
                player_1_obs[f"{i},{j}"] = 1
    return [player_0_obs, player_1_obs]