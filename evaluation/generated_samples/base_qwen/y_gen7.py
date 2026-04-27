import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to initialize the state
def get_initial_state():
    # Initialize the board as a dictionary with keys representing each cell
    # 'board' will be a list of lists to represent the triangular board
    board = [[None for _ in range(10)] for _ in range(10)]
    # Set the corners and edges
    board[0][0] = 'C'
    board[0][9] = 'C'
    board[9][0] = 'A'
    board[9][9] = 'A'
    board[4][0] = 'B'
    board[4][9] = 'B'
    board[5][0] = 'A'
    board[5][9] = 'A'
    board[6][0] = 'B'
    board[6][9] = 'B'
    board[7][0] = 'A'
    board[7][9] = 'A'
    board[8][0] = 'B'
    board[8][9] = 'B'
    board[9][1] = 'A'
    board[9][2] = 'A'
    board[9][3] = 'A'
    board[9][4] = 'A'
    board[9][5] = 'A'
    board[9][6] = 'A'
    board[9][7] = 'A'
    board[9][8] = 'A'
    board[9][9] = 'C'
    
    # Return the initial state
    return {'board': board}

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert the action string to a tuple of coordinates
    x, y = map(int, action.split(','))
    # Get the current player
    player = get_current_player(state)
    # Update the board with the player's move
    state['board'][y][x] = player
    # Return the new state
    return state

# Get the current player
def get_current_player(state: State) -> int:
    # The first player is Black (0)
    return 0 if state['turn'] == 0 else 1

# Get the player name
def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

# Get the rewards
def get_rewards(state: State) -> list[float]:
    # Check if the game is over
    if get_winner(state) is not None:
        return [1.0, 0.0] if get_winner(state) == 0 else [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Determine the winner
def get_winner(state: State) -> int | None:
    # Check all possible winning groups
    for side in ['A', 'B', 'C']:
        for i in range(10):
            if state['board'][i][0] == side and state['board'][i][9] == side:
                # Check if the group can connect to another side
                if state['board'][i][1] is not None and state['board'][i][1] == 'A':
                    if state['board'][i][2] is not None and state['board'][i][2] == 'B':
                        return 0 if side == 'A' else 1
                if state['board'][i][8] is not None and state['board'][i][8] == 'A':
                    if state['board'][i][7] is not None and state['board'][i][7] == 'B':
                        return 0 if side == 'A' else 1
                if state['board'][i][1] is not None and state['board'][i][1] == 'B':
                    if state['board'][i][2] is not None and state['board'][i][2] == 'C':
                        return 0 if side == 'B' else 1
                if state['board'][i][8] is not None and state['board'][i][8] == 'B':
                    if state['board'][i][7] is not None and state['board'][i][7] == 'C':
                        return 0 if side == 'B' else 1
    return None

# Get the legal actions
def get_legal_actions(state: State) -> list[Action]:
    # Get the current player
    player = get_current_player(state)
    # List to hold the legal actions
    legal_actions = []
    # Iterate through the board to find empty cells
    for i in range(10):
        for j in range(10):
            if state['board'][i][j] is None:
                legal_actions.append(f"{i},{j}")
    # Return the legal actions
    return legal_actions

# Get the observations
def get_observations(state: State) -> list[PlayerObservation]:
    # Create an observation for each player
    obs_black = {'board': copy.deepcopy(state['board']), 'turn': state['turn']}
    obs_white = {'board': copy.deepcopy(state['board']), 'turn': state['turn']}
    # Return the observations
    return [obs_black, obs_white]