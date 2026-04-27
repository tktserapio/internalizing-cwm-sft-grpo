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

# Helper function to create a new state from an existing one
def clone_state(state: State) -> State:
    return copy.deepcopy(state)

# Required Functions
def get_initial_state() -> State:
    # Initial state with an empty board
    return {
        'board': {},
        'current_player': 0,
        'winner': -4,
        'turn': 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Apply an action to the state and return the new state.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = clone_state(state)
    new_state['board'][action] = new_state['current_player']
    new_state['turn'] += 1
    new_state['current_player'] = 1 - new_state['current_player']

    # Check if the move completes a side
    if check_win(new_state):
        new_state['winner'] = new_state['current_player']
    
    return new_state

def check_win(state: State) -> bool:
    """
    Check if the current player has won the game.
    """
    board = state['board']
    current_player = state['current_player']
    
    # Check each side
    for side in ['A', 'B', 'C']:
        side_cells = [cell for cell in board if cell.startswith(side)]
        if len(side_cells) == 3 and all(board[cell] == current_player for cell in side_cells):
            return True
    
    return False

def get_current_player(state: State) -> int:
    """
    Return the current player (0 or 1), or -4 for terminal state.
    """
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """
    Return the name of the player.
    """
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> list[float]:
    """
    Return the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    if state['winner'] != -4:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Return legal actions for current state. Empty list if terminal.
    """
    board = state['board']
    current_player = state['current_player']
    legal_actions = []
    
    # Get all empty cells
    for cell in board:
        if board[cell] == -1:
            legal_actions.append(cell)
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Return [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    observations = []
    
    # Create observation for each player
    for player_id in range(2):
        observation = {}
        for cell, player in board.items():
            if player == player_id:
                observation[cell] = 1.0
            elif player == -1:
                observation[cell] = 0.5
            else:
                observation[cell] = 0.0
        observations.append(observation)
    
    return observations