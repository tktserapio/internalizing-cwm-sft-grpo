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

# Helper function to create a deep copy of the state
def deepcopy_state(state):
    return copy.deepcopy(state)

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial state with positions of players' units
    initial_state = {
        'board': [[None]*5 for _ in range(5)],
        'current_player': 0,
        'turn_count': 0,
        'stunned_units': []
    }
    # Place units for Player 0 (Blue)
    initial_state['board'][0][0] = {'color': 'Blue', 'position': (0, 0)}
    initial_state['board'][0][4] = {'color': 'Blue', 'position': (0, 4)}
    # Place units for Player 1 (Red)
    initial_state['board'][4][0] = {'color': 'Red', 'position': (4, 0)}
    initial_state['board'][4][4] = {'color': 'Red', 'position': (4, 4)}
    return initial_state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = deepcopy_state(state)
    if action == 'pass':
        new_state['current_player'] = 1 if new_state['current_player'] == 0 else 0
        new_state['turn_count'] += 1
        return new_state
    else:
        # Parse the action string
        source_position, target_position = action.split(' to ')
        source_row, source_col = map(int, source_position.split(','))
        target_row, target_col = map(int, target_position.split(','))
        
        # Check if the source position is valid
        if new_state['board'][source_row][source_col] is None:
            raise ValueError(f"Source position ({source_row}, {source_col}) is invalid.")
        
        # Check if the target position is valid
        if new_state['board'][target_row][target_col] is not None:
            raise ValueError(f"Target position ({target_row}, {target_col}) is occupied.")
        
        # Update the board
        new_state['board'][target_row][target_col] = new_state['board'][source_row][source_col]
        new_state['board'][source_row][source_col] = None
        
        # Handle stun mechanic
        for unit in new_state['stunned_units']:
            if unit['position'] == (target_row, target_col):
                new_state['stunned_units'].remove(unit)
        
        # Handle turn count
        new_state['turn_count'] += 1
        new_state['current_player'] = 1 if new_state['current_player'] == 0 else 0
        
        return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return ['Blue', 'Red'][player_id]

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['current_player'] == 0 and state['board'][2][2] is not None:
        return [1.0, 0.0]
    elif state['current_player'] == 1 and state['board'][2][2] is not None:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    if state['current_player'] == 0:
        for row, col in [(0, 0), (0, 4)]:
            if state['board'][row][col] is not None:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    target_row, target_col = row + dr, col + dc
                    if 0 <= target_row < 5 and 0 <= target_col < 5 and state['board'][target_row][target_col] is None:
                        legal_actions.append(f'move ({row},{col}) to ({target_row},{target_col})')
    else:
        for row, col in [(4, 0), (4, 4)]:
            if state['board'][row][col] is not None:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    target_row, target_col = row + dr, col + dc
                    if 0 <= target_row < 5 and 0 <= target_col < 5 and state['board'][target_row][target_col] is None:
                        legal_actions.append(f'move ({row},{col}) to ({target_row},{target_col})')
    
    # Add pass action if no legal moves
    if not legal_actions:
        legal_actions.append('pass')
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {
        'board': [[cell['color'] if cell is not None else None for cell in row] for row in state['board']],
        'current_player': state['current_player'],
        'turn_count': state['turn_count']
    }
    player_1_obs = deepcopy_state(player_0_obs)
    player_1_obs['current_player'] = 1 - state['current_player']
    return [player_0_obs, player_1_obs]