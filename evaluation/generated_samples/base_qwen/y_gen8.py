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

# Helper function to check if a move connects all three sides
def is_winner(state: State, player: int) -> bool:
    # This function would need to be implemented based on the specific logic of checking connections
    pass

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': {'A1': None, 'A2': None, 'A3': None, 'B1': None, 'B2': None, 'B3': None, 'C1': None, 'C2': None, 'C3': None},
        'current_player': 0,
        'turn': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    new_state['board'][action] = new_state['current_player']
    new_state['turn'] += 1
    new_state['current_player'] = 1 - new_state['current_player']
    
    # Check if the move makes the player a winner
    if is_winner(new_state, new_state['current_player']):
        new_state['winner'] = new_state['current_player']
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['winner'] is not None:
        return [1.0, -1.0] if state['winner'] == 0 else [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for cell in state['board']:
        if state['board'][cell] is None:
            legal_actions.append(cell)
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    for player in range(2):
        observation = {}
        for cell, player_id in state['board'].items():
            if player_id == player:
                observation[cell] = 1
            else:
                observation[cell] = 0
        observations.append(observation)
    return observations

# Helper function to check if a move connects all three sides
def is_winner(state: State, player: int) -> bool:
    # This function would need to be implemented based on the specific logic of checking connections
    # For simplicity, let's assume we can check each side independently
    board = state['board']
    corners = ['A1', 'A3', 'C1', 'C3']
    sides = [
        ['A1', 'A2', 'B1'], ['A2', 'B2'], ['B2', 'B3', 'C2'],
        ['A3', 'B3', 'C3'], ['C1', 'C2', 'B1'], ['C2', 'B2']
    ]
    
    for side in sides:
        if all(board[cell] == player for cell in side):
            return True
    
    for corner in corners:
        if board[corner] == player:
            return True
    
    return False