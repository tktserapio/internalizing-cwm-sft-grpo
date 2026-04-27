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
    # Initial positions for Blue (Player 0) and Red (Player 1)
    blue_units = [(0, 0), (0, 4)]
    red_units = [(4, 0), (4, 4)]
    center_square = (2, 2)
    
    # Initialize the state dictionary
    state = {
        'blue_units': blue_units,
        'red_units': red_units,
        'current_player': 0,
        'turn_count': 0,
        'center_square_occupied': False,
        'stunned_units': [],
        'game_over': False
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = deepcopy_state(state)
    if action == "pass":
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    
    # Parse the action string
    source, target = action.split(" to ")
    source_row, source_col = map(int, source.split(","))
    target_row, target_col = map(int, target.split(","))
    
    # Check if the action is valid
    if (source_row, source_col) not in new_state['blue_units'] and (source_row, source_col) not in new_state['red_units']:
        raise ValueError(f"Invalid source position: {source}")
    if (target_row, target_col) in new_state['blue_units'] or (target_row, target_col) in new_state['red_units']:
        raise ValueError(f"Target position is occupied: {target}")
    
    # Apply the move
    new_state['blue_units'].remove((source_row, source_col))
    new_state['blue_units'].append((target_row, target_col))
    
    # Check for stun condition
    for unit in new_state['blue_units']:
        if abs(unit[0] - target_row) + abs(unit[1] - target_col) <= 1:
            new_state['stunned_units'].append(unit)
    
    # Update the current player
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    # Check if the center square is occupied
    if (2, 2) in new_state['blue_units']:
        new_state['game_over'] = True
        new_state['center_square_occupied'] = True
    elif (2, 2) in new_state['red_units']:
        new_state['game_over'] = True
        new_state['center_square_occupied'] = True
    
    # Increment the turn count
    new_state['turn_count'] += 1
    
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
    if state['game_over']:
        if state['center_square_occupied']:
            if state['current_player'] == 0:
                return [1.0, 0.0]
            else:
                return [0.0, 1.0]
        else:
            return [0.5, 0.5]  # Draw
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    if state['current_player'] == 0:
        for unit in state['blue_units']:
            for target in [(unit[0] + 1, unit[1]), (unit[0] - 1, unit[1]), (unit[0], unit[1] + 1), (unit[0], unit[1] - 1), (unit[0] + 1, unit[1] + 1), (unit[0] + 1, unit[1] - 1), (unit[0] - 1, unit[1] + 1), (unit[0] - 1, unit[1] - 1)]:
                if 0 <= target[0] <= 4 and 0 <= target[1] <= 4 and target not in state['blue_units'] + state['red_units']:
                    legal_actions.append(f"move ({unit[0]}, {unit[1]}) to ({target[0]}, {target[1]})")
    else:
        for unit in state['red_units']:
            for target in [(unit[0] + 1, unit[1]), (unit[0] - 1, unit[1]), (unit[0], unit[1] + 1), (unit[0], unit[1] - 1), (unit[0] + 1, unit[1] + 1), (unit[0] + 1, unit[1] - 1), (unit[0] - 1, unit[1] + 1), (unit[0] - 1, unit[1] - 1)]:
                if 0 <= target[0] <= 4 and 0 <= target[1] <= 4 and target not in state['blue_units'] + state['red_units']:
                    legal_actions.append(f"move ({unit[0]}, {unit[1]}) to ({target[0]}, {target[1]})")
    if not legal_actions:
        legal_actions.append("pass")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {
        'units': state['blue_units'],
        'stunned_units': state['stunned_units'],
        'turn_count': state['turn_count'],
        'center_square_occupied': state['center_square_occupied']
    }
    player_1_obs = {
        'units': state['red_units'],
        'stunned_units': state['stunned_units'],
        'turn_count': state['turn_count'],
        'center_square_occupied': state['center_square_occupied']
    }
    return [player_0_obs, player_1_obs]