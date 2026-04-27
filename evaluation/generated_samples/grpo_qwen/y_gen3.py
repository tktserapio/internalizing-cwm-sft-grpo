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

# Helper function to create an initial state
def get_initial_state() -> State:
    # Initial state with an empty board
    return {
        'board': {},
        'current_player': 0,
        'turn': 0,
        'winner': None
    }

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action to coordinates
    row, col = map(int, action.split(','))

    # Check if the action is valid
    if row < 0 or col < 0 or row >= len(state['board']) or col >= len(state['board'][row]):
        raise ValueError("Invalid action")

    # Update the board with the new stone
    state['board'][row][col] = state['current_player'] + 1

    # Switch the current player
    state['current_player'] = (state['current_player'] + 1) % 2
    state['turn'] += 1

    # Check for win condition
    check_win_condition(state)

    return state

# Function to check if there's a winner
def check_win_condition(state: State):
    board = state['board']
    rows = len(board)
    cols = len(board[0])
    directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

    for i in range(rows):
        for j in range(cols):
            if board[i][j] == 0:
                continue
            for di, dj in directions:
                x, y = i + di, j + dj
                while 0 <= x < rows and 0 <= y < cols and board[x][y] == 0:
                    x, y = x + di, y + dj
                if 0 <= x < rows and 0 <= y < cols and board[x][y] == board[i][j]:
                    return
    state['winner'] = state['current_player']

# Function to get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

# Function to get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state['winner'] is not None:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Function to get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    board = state['board']
    rows = len(board)
    cols = len(board[0])
    legal_actions = []
    for i in range(rows):
        for j in range(cols):
            if board[i][j] == 0:
                legal_actions.append(f"{i},{j}")
    return legal_actions

# Function to get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    board = state['board']
    rows = len(board)
    cols = len(board[0])
    observations = []
    for i in range(rows):
        for j in range(cols):
            if board[i][j] == 0:
                continue
            observation = {'stone': board[i][j], 'position': f"{i},{j}"}
            observations.append(observation)
    return observations