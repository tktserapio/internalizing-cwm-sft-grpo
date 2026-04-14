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

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initial state with players' positions and other relevant data
    return {
        'current_player': 0,
        'board': [
            ['B', None, None, None, 'R'],
            [None, None, None, None, None],
            [None, None, 'C', None, None],
            [None, None, None, None, None],
            ['B', None, None, None, 'R']
        ],
        'turn_count': 0,
        'stunned_units': []
    }

# Function to apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    # Create a deep copy of the current state to avoid mutating it
    new_state = copy.deepcopy(state)
    # Update the board based on the action
    if action.startswith('move'):
        source, target = action.split()[1:]
        source = tuple(map(int, source[1:-1].split(',')))
        target = tuple(map(int, target[1:-1].split(',')))
        new_state['board'][source[0]][source[1]] = None
        new_state['board'][target[0]][target[1]] = 'B' if state['current_player'] == 0 else 'R'
    elif action == 'pass':
        new_state['current_player'] = (state['current_player'] + 1) % 2
    else:
        raise ValueError(f"Invalid action: {action}")
    
    # Check for stun condition
    for unit in state['stunned_units']:
        if unit == source or unit == target:
            new_state['board'][unit[0]][unit[1]] = 'B' if state['current_player'] == 0 else 'R'
            new_state['stunned_units'].remove(unit)
    
    # Increment turn count
    new_state['turn_count'] += 1
    
    return new_state

# Function to determine the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Blue' if player_id == 0 else 'Red'

# Function to get the rewards for each player
def get_rewards(state: State) -> list[float]:
    # In this simple implementation, we assume there's no running reward tracking
    return [0.0, 0.0]

# Function to get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    current_player = state['current_player']
    board = state['board']
    current_player_units = [pos for pos, unit in enumerate(board) if unit == 'B' if current_player == 0 else 'R']
    legal_actions = []

    for unit in current_player_units:
        row, col = unit // 5, unit % 5
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 5 and 0 <= new_col < 5 and board[new_row * 5 + new_col] is None:
                legal_actions.append(f'move ({row},{col}) to ({new_row},{new_col})')
            elif board[new_row * 5 + new_col] != 'B' if current_player == 0 else 'R':
                legal_actions.append(f'move ({row},{col}) to ({new_row},{new_col})')

    if not legal_actions and len(state['stunned_units']) > 0:
        legal_actions.append('pass')

    return legal_actions

# Function to get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    current_player = state['current_player']
    board = state['board']
    observations = [{'observation': board[i]} for i in range(25) if board[i] is not None]
    return observations

# Example usage
initial_state = get_initial_state()
print("Initial State:", initial_state)

# Apply an action
action = 'move (0,0) to (1,1)'
new_state = apply_action(initial_state, action)
print("After Action:", new_state)

# Get current player
current_player = get_current_player(new_state)
print("Current Player:", get_player_name(current_player))

# Get legal actions
legal_actions = get_legal_actions(new_state)
print("Legal Actions:", legal_actions)

# Get observations
observations = get_observations(new_state)
print("Observations:", observations)