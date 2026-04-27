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
    # Initial state with positions of players and center square as False (not yet occupied)
    initial_state = {
        'blue_units': [(0, 0), (0, 4)],
        'red_units': [(4, 0), (4, 4)],
        'center_occupied': False,
        'current_player': 0,
        'turn_count': 0,
        'stunned_units': [],
        'game_over': False
    }
    return initial_state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = deepcopy_state(state)
    
    # Parse the action string
    action_parts = action.split(' ')
    if action_parts[0] == 'move':
        from_pos = tuple(map(int, action_parts[1][1:-1].split(',')))
        to_pos = tuple(map(int, action_parts[2][1:-1].split(',')))
        
        # Check if the move is valid
        if from_pos in new_state['blue_units'] or from_pos in new_state['red_units']:
            if new_state['current_player'] == 0:
                new_state['blue_units'].remove(from_pos)
                new_state['blue_units'].append(to_pos)
            else:
                new_state['red_units'].remove(from_pos)
                new_state['red_units'].append(to_pos)
            
            # Check for stun condition
            for unit in new_state['blue_units'] + new_state['red_units']:
                if abs(unit[0] - to_pos[0]) <= 1 and abs(unit[1] - to_pos[1]) <= 1:
                    new_state['stunned_units'].append(unit)
                    break
            
            # Remove stunned units from the list
            new_state['stunned_units'] = [unit for unit in new_state['stunned_units'] if unit not in new_state['blue_units'] + new_state['red_units']]
            
            # Check if the center square is occupied
            if to_pos == (2, 2):
                new_state['game_over'] = True
                new_state['center_occupied'] = True
                new_state['current_player'] = -4
            else:
                new_state['current_player'] = 1 - new_state['current_player']
                new_state['turn_count'] += 1
                
                # Check if the other player has no legal moves
                if not get_legal_actions(new_state):
                    new_state['current_player'] = -4
    elif action_parts[0] == 'pass':
        new_state['current_player'] = 1 - new_state['current_player']
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
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['game_over']:
        if state['center_occupied']:
            return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
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
            # Check for possible moves
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if abs(i) + abs(j) <= 1 and (i != 0 or j != 0):
                        to_pos = (unit[0] + i, unit[1] + j)
                        if to_pos in state['blue_units'] or to_pos in state['red_units']:
                            continue
                        if to_pos not in state['stunned_units']:
                            legal_actions.append(f'move {unit} to {to_pos}')
            # Check for pass
            if not any(unit in state['blue_units'] for unit in state['blue_units']) and not any(unit in state['red_units'] for unit in state['red_units']):
                legal_actions.append('pass')
    else:
        for unit in state['red_units']:
            # Check for possible moves
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if abs(i) + abs(j) <= 1 and (i != 0 or j != 0):
                        to_pos = (unit[0] + i, unit[1] + j)
                        if to_pos in state['blue_units'] or to_pos in state['red_units']:
                            continue
                        if to_pos not in state['stunned_units']:
                            legal_actions.append(f'move {unit} to {to_pos}')
            # Check for pass
            if not any(unit in state['blue_units'] for unit in state['blue_units']) and not any(unit in state['red_units'] for unit in state['red_units']):
                legal_actions.append('pass')
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    blue_obs = {
        'units': state['blue_units'],
        'stunned_units': state['stunned_units'],
        'turn_count': state['turn_count'],
        'center_occupied': state['center_occupied'],
        'current_player': state['current_player']
    }
    red_obs = {
        'units': state['red_units'],
        'stunned_units': state['stunned_units'],
        'turn_count': state['turn_count'],
        'center_occupied': state['center_occupied'],
        'current_player': state['current_player']
    }
    return [blue_obs, red_obs]