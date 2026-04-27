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
        'blue_units': [(0, 0), (0, 4)],
        'red_units': [(4, 0), (4, 4)],
        'current_player': 0,
        'turn_count': 0,
        'center_square_occupied': False
    }
    return initial_state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = deepcopy_state(state)
    if action == 'pass':
        return new_state
    
    # Parse the action
    src, dest = action.split(' to ')
    src_row, src_col = map(int, src.split(','))
    dest_row, dest_col = map(int, dest.split(','))

    # Check if the source position is valid
    if (src_row, src_col) not in new_state['blue_units'] + new_state['red_units']:
        raise ValueError("Invalid source position")
    
    # Check if the destination position is valid
    if (dest_row, dest_col) not in new_state['blue_units'] + new_state['red_units']:
        raise ValueError("Destination position is occupied")

    # Apply the move
    src_unit = (src_row, src_col)
    dest_unit = (dest_row, dest_col)
    new_state['blue_units'].remove(src_unit)
    new_state['blue_units'].append(dest_unit)
    
    # Update the current player
    new_state['current_player'] = 1 if new_state['current_player'] == 0 else 0
    
    # Check for stun
    for unit in new_state['blue_units'] + new_state['red_units']:
        if unit == src_unit:
            continue
        if abs(unit[0] - dest_row) <= 1 and abs(unit[1] - dest_col) <= 1:
            new_state['red_units'].remove(unit)
            new_state['red_units'].append((unit[0], unit[1]))
            new_state['center_square_occupied'] = True
            break
    
    # Increment the turn count
    new_state['turn_count'] += 1
    
    # Check for win condition
    if dest_unit == (2, 2):
        new_state['center_square_occupied'] = True
        new_state['winner'] = new_state['current_player']
    
    # Check for draw condition
    if new_state['turn_count'] >= 50:
        new_state['winner'] = -4
    
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
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['winner'] != -4:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    if state['current_player'] == 0:
        blue_units = state['blue_units']
        for src_unit in blue_units:
            for dest_row in range(5):
                for dest_col in range(5):
                    if (dest_row, dest_col) not in blue_units + state['red_units']:
                        legal_actions.append(f'move {src_unit} to ({dest_row},{dest_col})')
    else:
        red_units = state['red_units']
        for src_unit in red_units:
            for dest_row in range(5):
                for dest_col in range(5):
                    if (dest_row, dest_col) not in blue_units + state['red_units']:
                        legal_actions.append(f'move {src_unit} to ({dest_row},{dest_col})')
    if not legal_actions and state['current_player'] == 0:
        legal_actions.append('pass')
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {
        'units': state['blue_units'],
        'stunned_units': [],
        'current_player': state['current_player']
    }
    player_1_obs = {
        'units': state['red_units'],
        'stunned_units': [],
        'current_player': state['current_player']
    }
    return [player_0_obs, player_1_obs]