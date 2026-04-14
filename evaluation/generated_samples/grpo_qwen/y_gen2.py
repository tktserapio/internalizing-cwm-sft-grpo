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
    # Extracting the board from the state
    board = state['board']
    # Checking each side for a complete connection
    for side in ['A', 'B', 'C']:
        # Getting the cells of the current side
        side_cells = board[side]
        # Counting how many of these cells belong to the current player
        count = sum(1 for cell in side_cells if cell == player)
        # If all cells are occupied by the current player, it's a win
        if count == len(side_cells):
            return True
    return False

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': {
            'A': ['1', '3', '6'],
            'B': ['2', '5', '9'],
            'C': ['6', '7', '8', '9']
        },
        'current_player': 0,
        'turn': 0,
        'size': 4
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    # Convert action string to coordinates
    row, col = map(int, action.split(','))
    # Update the board with the new action
    new_state['board'][f'A{row + 1}'].append(str(new_state['current_player']))
    new_state['board'][f'B{col + 1}'].append(str(new_state['current_player']))
    new_state['board'][f'C{max(row, col) + 1}'].append(str(new_state['current_player']))
    # Switch the current player
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    new_state['turn'] += 1
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f'Player {player_id + 1}'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if is_winner(state, 0):
        return [1.0, 0.0]
    elif is_winner(state, 1):
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    # Check if the board is full
    if len(state['board']['A']) + len(state['board']['B']) + len(state['board']['C']) >= state['size'] * state['size']:
        return []
    # Generate all possible moves
    legal_actions = []
    for i in range(state['size']):
        for j in range(state['size']):
            if str(state['current_player']) not in state['board'][f'A{i + 1}'] and str(state['current_player']) not in state['board'][f'B{j + 1}'] and str(state['current_player']) not in state['board'][f'C{max(i, j) + 1}']:
                legal_actions.append(f'{i},{j}')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    for player_id in [0, 1]:
        observation = {}
        observation['board'] = state['board']
        observation['current_player'] = state['current_player']
        observation['turn'] = state['turn']
        observation['size'] = state['size']
        observation['player_id'] = player_id
        observations.append(observation)
    return observations