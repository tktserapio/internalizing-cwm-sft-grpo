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
        'current_player': 0,  # Player 0 is Black
        'turn': 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    row, col = map(int, action.split(','))

    # Convert 0-indexed coordinates to 1-indexed for the board
    row += 1
    col += 1

    # Check if the action is valid
    if row < 1 or row > 4 or col < 1 or col > 4:
        raise ValueError("Invalid action")

    # Apply the action
    new_state['board'][f'A{row}{col}'] = 'B' if new_state['current_player'] == 0 else 'W'
    new_state['current_player'] = 1 - new_state['current_player']
    new_state['turn'] += 1

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In a perfect information game like Y, there's no need to track rewards
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    legal_actions = []

    for row in range(1, 5):
        for col in range(1, 5):
            if board.get(f'A{row}{col}') is None:
                legal_actions.append(f'{row},{col}')

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    current_player = state['current_player']
    observations = []

    # Create observations for each player
    player_0_obs = {}
    player_1_obs = {}

    for cell, player in board.items():
        if player is None:
            continue
        if player == 'B':
            player_0_obs[cell] = True
        elif player == 'W':
            player_1_obs[cell] = True

    observations.append(player_0_obs)
    observations.append(player_1_obs)

    return observations