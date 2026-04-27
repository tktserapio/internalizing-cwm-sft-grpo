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

# Helper function to create an initial state
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': {
            'A1': None,
            'A2': None,
            'A3': None,
            'A4': None,
            'B1': None,
            'B2': None,
            'B3': None,
            'B4': None,
            'C1': None,
            'C2': None,
            'C3': None,
            'C4': None
        },
        'current_player': 0  # Black starts
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    new_state['board'][action] = new_state['current_player']
    new_state['current_player'] = 1 - new_state['current_player']
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In this simple implementation, we assume a win gives a reward of 1.0
    # and a loss gives a reward of 0.0. Draws are not possible in this setup.
    if is_winner(state, 0):
        return [1.0, 0.0]
    elif is_winner(state, 1):
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Determine if a player has won
def is_winner(state: State, player_id: int) -> bool:
    """Determine if a player has formed a connected group that touches all three sides."""
    board = state['board']
    corners = ['A1', 'A4', 'C1', 'C4']
    edges = [
        ('A1', 'A2'), ('A2', 'A3'), ('A3', 'A4'),
        ('B1', 'B2'), ('B2', 'B3'), ('B3', 'B4'),
        ('C1', 'C2'), ('C2', 'C3'), ('C3', 'C4')
    ]
    
    def is_connected(cell: str, player_id: int) -> bool:
        neighbors = [
            ('A1', 'A2'), ('A2', 'A3'), ('A3', 'A4'),
            ('B1', 'B2'), ('B2', 'B3'), ('B3', 'B4'),
            ('C1', 'C2'), ('C2', 'C3'), ('C3', 'C4'),
            ('A1', 'B1'), ('A2', 'B2'), ('A3', 'B3'), ('A4', 'B4'),
            ('B1', 'C1'), ('B2', 'C2'), ('B3', 'C3'), ('B4', 'C4')
        ]
        for neighbor in neighbors:
            if board[cell] == player_id and board[neighbor[0]] == player_id and board[neighbor[1]] == player_id:
                return True
        return False
    
    for corner in corners:
        if board[corner] == player_id and is_connected(corner, player_id):
            return True
    for edge in edges:
        if board[edge[0]] == player_id and board[edge[1]] == player_id and is_connected(edge[0], player_id):
            return True
    return False

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    legal_actions = []
    for cell in board.keys():
        if board[cell] is None:
            legal_actions.append(cell)
    return legal_actions

# Get observations for both players
def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    player_0_obs = {}
    player_1_obs = {}
    for cell, player in board.items():
        if player is None:
            continue
        if player == 0:
            player_0_obs[cell] = 1
        else:
            player_1_obs[cell] = 1
    return [player_0_obs, player_1_obs]