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
        'winner': None
    }

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    """
    Apply an action to the current state and return the new state.
    """
    # Convert action to coordinates
    row, col = map(int, action.split(','))

    # Check if the action is valid
    if row < 0 or row >= 4 or col < 0 or col >= 4:
        raise ValueError("Invalid action")

    # Create a copy of the state to avoid mutating the original
    new_state = state.copy()
    new_state['board'][f'{row},{col}'] = new_state['current_player']
    new_state['current_player'] = 1 - new_state['current_player']

    # Check for winner
    winner = check_winner(new_state)
    if winner:
        new_state['winner'] = winner
    return new_state

# Function to check for a winner
def check_winner(state: State) -> int:
    """
    Check if there's a winner based on the current state.
    """
    board = state['board']
    corners = ['0,0', '3,3', '3,0', '0,3']
    edges = [
        ('0,0', '0,1', '0,2', '0,3'),
        ('0,1', '1,1', '2,1', '3,1'),
        ('0,2', '1,2', '2,2', '3,2'),
        ('0,3', '0,4', '1,4', '2,4', '3,4'),
        ('1,0', '2,0', '3,0'),
        ('1,3', '2,3', '3,3')
    ]

    for edge in edges:
        if len(set(board[cell] for cell in edge)) == 1:
            return board[edge[0]]

    for corner in corners:
        if len(set(board[cell] for cell in [corner, *get_adjacent_cells(corner)])) == 1:
            return board[corner]

    return None

# Function to get legal actions
def get_legal_actions(state: State) -> List[Action]:
    """
    Get legal actions for the current state.
    """
    board = state['board']
    legal_actions = []
    for row in range(4):
        for col in range(4):
            if f'{row},{col}' not in board:
                legal_actions.append(f'{row},{col}')
    return legal_actions

# Function to get observations
def get_observations(state: State) -> List[PlayerObservation]:
    """
    Get observations for each player.
    """
    board = state['board']
    observations = []
    for player_id in range(2):
        observation = {}
        for row in range(4):
            for col in range(4):
                cell = f'{row},{col}'
                if cell in board:
                    observation[cell] = board[cell]
                else:
                    observation[cell] = None
        observations.append(observation)
    return observations

# Function to get current player
def get_current_player(state: State) -> int:
    """
    Get the current player.
    """
    return state['current_player']

# Function to get player name
def get_player_name(player_id: int) -> str:
    """
    Get the name of the player.
    """
    return 'Black' if player_id == 0 else 'White'

# Function to get rewards
def get_rewards(state: State) -> List[float]:
    """
    Get rewards for the current state.
    """
    winner = state['winner']
    if winner is None:
        return [0.0, 0.0]
    elif winner == 0:
        return [1.0, 0.0]
    else:
        return [0.0, 1.0]