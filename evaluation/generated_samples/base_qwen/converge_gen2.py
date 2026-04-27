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

def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial positions for Blue and Red players
    blue_units = [(0, 0), (0, 4)]
    red_units = [(4, 0), (4, 4)]
    return {
        'blue_units': blue_units,
        'red_units': red_units,
        'current_player': 0,
        'turn_count': 0,
        'center_square_occupied': False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    
    # Parse the action
    source, target = action.split(' to ')
    sr, sc = map(int, source.split(','))
    tr, tc = map(int, target.split(','))
    
    # Check if the action is valid
    if not (0 <= sr < 5 and 0 <= sc < 5 and 0 <= tr < 5 and 0 <= tc < 5):
        raise ValueError("Invalid action: Source or target out of bounds.")
    
    if (sr, sc) not in state['blue_units'] + state['red_units']:
        raise ValueError("Invalid action: Source square is not occupied.")
    
    if (tr, tc) in state['blue_units'] + state['red_units']:
        raise ValueError("Invalid action: Target square is occupied.")
    
    # Apply the action
    if action.startswith('move'):
        new_state['blue_units'] = [
            (sr, sc) if (sr, sc) == (tr, tc) else unit for unit in state['blue_units']
        ]
        new_state['red_units'] = [
            (tr, tc) if (tr, tc) == (sr, sc) else unit for unit in state['red_units']
        ]
    elif action == 'pass':
        new_state['current_player'] = 1 if state['current_player'] == 0 else 0
        new_state['turn_count'] += 1
    else:
        raise ValueError("Invalid action: Unknown action.")
    
    # Handle stun mechanic
    if action.startswith('move'):
        for unit in state['blue_units'] + state['red_units']:
            if abs(unit[0] - tr) + abs(unit[1] - tc) == 1:
                new_state['blue_units'] = [
                    (unit[0], unit[1]) if (unit[0], unit[1]) != (tr, tc) else (tr, tc)
                    for unit in state['blue_units']
                ]
                new_state['red_units'] = [
                    (unit[0], unit[1]) if (unit[0], unit[1]) != (tr, tc) else (tr, tc)
                    for unit in state['red_units']
                ]
                break
    
    # Check if the center square is occupied
    if (2, 2) in state['blue_units']:
        new_state['center_square_occupied'] = True
        new_state['current_player'] = -4  # Terminal state
    
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

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    if state['center_square_occupied']:
        return [-1.0, 1.0]  # Blue wins
    elif state['turn_count'] >= 50:
        return [0.0, 0.0]  # Draw
    else:
        return [0.0, 0.0]  # No winner yet

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    
    # Get current player
    current_player = state['current_player']
    
    # Get units for the current player
    units = state['blue_units'] if current_player == 0 else state['red_units']
    
    # Check for possible moves
    for unit in units:
        sr, sc = unit
        for dr, dc in [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]:
            tr, tc = sr + dr, sc + dc
            if 0 <= tr < 5 and 0 <= tc < 5 and (tr, tc) not in state['blue_units'] + state['red_units']:
                legal_actions.append(f'move ({sr},{sc}) to ({tr},{tc})')
    
    # Check if the current player can pass
    if len(legal_actions) == 0:
        legal_actions.append('pass')
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    blue_units = state['blue_units']
    red_units = state['red_units']
    
    player_0_obs = {
        'units': blue_units,
        'stunned_units': [],
        'center_square_occupied': state['center_square_occupied'],
        'turn_count': state['turn_count'],
        'current_player': state['current_player']
    }
    
    player_1_obs = {
        'units': red_units,
        'stunned_units': [],
        'center_square_occupied': state['center_square_occupied'],
        'turn_count': state['turn_count'],
        'current_player': state['current_player']
    }
    
    return [player_0_obs, player_1_obs]