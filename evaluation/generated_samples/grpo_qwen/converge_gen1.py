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

# Helper function to create a state dictionary
def create_state() -> State:
    return {
        'board': [[None]*5 for _ in range(5)],
        'current_player': 0,
        'turn_count': 0,
        'stunned_units': [],
        'winner': None
    }

# Required Functions
def get_initial_state() -> State:
    # Initial state setup
    state = create_state()
    state['board'][0][0] = {'color': 'blue', 'unit': 1}
    state['board'][0][4] = {'color': 'blue', 'unit': 1}
    state['board'][4][0] = {'color': 'red', 'unit': 1}
    state['board'][4][4] = {'color': 'red', 'unit': 1}
    return state

def apply_action(state: State, action: Action) -> State:
    # Apply the action to the state
    new_state = create_state()
    new_state.update(state)
    
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    
    # Parse the action
    source, target = action.split(' to ')
    sr, sc = map(int, source.split(','))
    tr, tc = map(int, target.split(','))
    
    # Check if the action is valid
    if new_state['board'][sr][sc] is None:
        return new_state
    
    unit = new_state['board'][sr][sc]
    if unit['color'] != new_state['current_player']:
        return new_state
    
    # Move the unit
    new_state['board'][sr][sc] = None
    new_state['board'][tr][tc] = unit
    
    # Check for stun
    for x, y in [(sr-1, sc-1), (sr-1, sc), (sr-1, sc+1), (sr, sc-1), (sr, sc+1), (sr+1, sc-1), (sr+1, sc), (sr+1, sc+1)]:
        if 0 <= x < 5 and 0 <= y < 5 and new_state['board'][x][y] is not None and new_state['board'][x][y]['color'] != new_state['current_player']:
            new_state['stunned_units'].append((x, y))
    
    # Remove stunned units
    new_state['stunned_units'] = [(x, y) for x, y in new_state['stunned_units'] if (x, y) not in [(tr, tc)]]
    
    # Update turn count
    new_state['turn_count'] += 1
    
    # Check for win condition
    if (tr, tc) == (2, 2):
        new_state['winner'] = new_state['current_player']
    
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    return new_state

def get_current_player(state: State) -> int:
    return state['current_player']

def get_player_name(player_id: int) -> str:
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> List[float]:
    if state['winner'] is not None:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    if state['winner'] is not None:
        return []
    
    current_player = state['current_player']
    legal_actions = []
    
    for row in range(5):
        for col in range(5):
            if state['board'][row][col] is not None and state['board'][row][col]['color'] == current_player:
                for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    nx, ny = row + dx, col + dy
                    if 0 <= nx < 5 and 0 <= ny < 5 and state['board'][nx][ny] is None:
                        legal_actions.append(f'move ({row},{col}) to ({nx},{ny})')
    
    if not legal_actions and len(state['stunned_units']) > 0:
        for x, y in state['stunned_units']:
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 5 and 0 <= ny < 5 and state['board'][nx][ny] is None:
                    legal_actions.append(f'move ({x},{y}) to ({nx},{ny})')
    
    if not legal_actions:
        return ['pass']
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    observations = []
    for row in range(5):
        for col in range(5):
            if state['board'][row][col] is not None:
                unit = state['board'][row][col]
                color = 'blue' if unit['color'] == 0 else 'red'
                position = f'({row},{col})'
                observations.append({
                    'position': position,
                    'color': color,
                    'stunned': (row, col) in state['stunned_units']
                })
    return observations