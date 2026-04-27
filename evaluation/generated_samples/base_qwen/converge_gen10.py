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
    # Initial positions for Blue and Red players
    blue_units = [(0, 0), (0, 4)]
    red_units = [(4, 0), (4, 4)]
    # Initial state dictionary
    state = {
        'blue_units': blue_units,
        'red_units': red_units,
        'current_player': 0,
        'turn_count': 0,
        'center_square_occupied': False
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = deepcopy_state(state)
    if action == 'pass':
        return new_state
    
    # Parse the action string
    source, target = action.split(' to ')
    source = tuple(map(int, source.split(',')))
    target = tuple(map(int, target.split(',')))
    
    # Check if the action is valid
    if not (0 <= source[0] < 5 and 0 <= source[1] < 5 and 0 <= target[0] < 5 and 0 <= target[1] < 5):
        raise ValueError("Invalid move")
    
    # Move the unit
    unit = new_state['blue_units'] if new_state['current_player'] == 0 else new_state['red_units']
    for i, pos in enumerate(unit):
        if pos == source:
            unit[i] = target
            break
    
    # Check if the center square is occupied
    if target == (2, 2):
        new_state['center_square_occupied'] = True
        new_state['current_player'] = -4  # Terminal state
    
    # Check for stun
    for unit_pos in unit:
        if abs(unit_pos[0] - target[0]) + abs(unit_pos[1] - target[1]) == 1:
            new_state['red_units'] if new_state['current_player'] == 0 else new_state['blue_units'][unit.index(unit_pos)] = (-1, -1)  # Stunned unit
            new_state['turn_count'] += 1  # Increment turn count
    
    new_state['current_player'] = 1 if new_state['current_player'] == 0 else 0
    new_state['turn_count'] += 1  # Increment turn count
    
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
    if state['center_square_occupied']:
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    if state['current_player'] == 0:
        units = state['blue_units']
    else:
        units = state['red_units']
    
    for unit in units:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx != 0 or dy != 0:
                    target = (unit[0] + dx, unit[1] + dy)
                    if 0 <= target[0] < 5 and 0 <= target[1] < 5 and (target not in units and target != (-1, -1)):
                        legal_actions.append(f'move {unit} to {target}')
    if not legal_actions:
        legal_actions.append('pass')
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    blue_obs = {'units': state['blue_units'], 'stunned': []}
    red_obs = {'units': state['red_units'], 'stunned': []}
    for unit in state['red_units']:
        if unit == (-1, -1):
            red_obs['stunned'].append(unit)
    for unit in state['blue_units']:
        if unit == (-1, -1):
            blue_obs['stunned'].append(unit)
    return [blue_obs, red_obs]