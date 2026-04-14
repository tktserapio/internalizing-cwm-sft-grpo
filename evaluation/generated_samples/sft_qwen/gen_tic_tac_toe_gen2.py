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
    # Initialize the game state with an empty 6x6 board
    board = np.zeros((6, 6))
    return {
        'board': board,
        'current_player': 0,  # Player 'x' starts first
        'winner': None,  # No player has won yet
        'turn': 0  # Track the number of moves made
    }

# Function to apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    # Convert action string to row, col indices
    row, col = map(int, action.split(','))

    # Check if the action is valid
    if state['board'][row][col] != 0:
        raise ValueError("Invalid action: Cell already occupied")

    # Update the board with the current player's mark
    state['board'][row][col] = state['current_player'] + 1  # Mark 'x' as 1, 'o' as 2

    # Switch to the next player
    state['current_player'] = (state['current_player'] + 1) % 2

    # Increment the turn count
    state['turn'] += 1

    # Check if there's a winner or a draw
    if check_winner(state):
        state['winner'] = state['current_player']
    elif state['turn'] == 36:
        state['winner'] = None

    return state

# Function to check if there's a winner
def check_winner(state: State) -> bool:
    board = state['board']

    # Check rows and columns
    for i in range(6):
        if np.all(board[i] == (state['current_player'] + 1)) or \
           np.all(board[:, i] == (state['current_player'] + 1)):
            return True

    # Check diagonals
    if np.all(np.diag(board) == (state['current_player'] + 1)) or \
       np.all(np.diag(np.fliplr(board)) == (state['current_player'] + 1)):
        return True

    return False

# Function to get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return 'x' if player_id == 0 else 'o'

# Function to get the rewards per player
def get_rewards(state: State) -> list[float]:
    if state['winner'] is not None:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Function to get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    board = state['board']
    current_player = state['current_player']
    legal_actions = []

    for row in range(6):
        for col in range(6):
            if board[row][col] == 0:
                legal_actions.append(f"{row},{col}")

    return legal_actions

# Function to get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    board = state['board']
    current_player = state['current_player']
    observations = []

    # Create a dictionary to store the observation for each player
    observation = {
        'board': board,
        'current_player': get_player_name(current_player),
        'legal_actions': get_legal_actions(state)
    }
    observations.append(observation)

    return observations