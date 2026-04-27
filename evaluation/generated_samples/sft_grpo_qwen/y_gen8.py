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
            'C1': None,
            'C2': None,
            'C3': None
        },
        'current_player': 0  # Black starts
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = new_state['current_player']
    new_state['current_player'] = 1 - player_id  # Switch player
    cell = action.split(',')
    row, col = int(cell[0]), int(cell[1])
    
    # Convert coordinates to board representation
    if row == 0:
        side = 'A'
        offset = 1
    elif row == 1:
        side = 'B'
        offset = 2
    else:
        side = 'C'
        offset = 3
    
    cell_key = f"{side}{offset + col}"
    
    new_state['board'][cell_key] = player_id
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In this simple implementation, we assume the game ends when one player wins
    # and return a reward based on that.
    board = state['board']
    black_stones = sum(1 for stone in board.values() if stone == 0)
    white_stones = sum(1 for stone in board.values() if stone == 1)
    
    if black_stones > white_stones:
        return [1.0, 0.0]
    elif white_stones > black_stones:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    legal_actions = []
    for cell, player in board.items():
        if player is None:
            legal_actions.append(cell)
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    player_0_obs = {}
    player_1_obs = {}
    
    for cell, player in board.items():
        if player is None:
            continue
        player_id = player
        if player_id == 0:
            player_0_obs[cell] = True
        else:
            player_1_obs[cell] = True
    
    return [player_0_obs, player_1_obs]