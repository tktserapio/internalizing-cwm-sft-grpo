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
        'board': [
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', 'B', 'R', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ']
        ],
        'current_player': 0,
        'turn_count': 0,
        'stunned_units': []
    }

# Required Functions
def get_initial_state() -> State:
    return create_state()

def apply_action(state: State, action: Action) -> State:
    # Parse the action
    r1, c1, r2, c2 = map(int, action.split(' ')[1:])
    
    # Update the board
    board = state['board']
    board[r1][c1], board[r2][c2] = board[r2][c2], board[r1][c1]
    
    # Update the current player
    state['current_player'] = 1 - state['current_player']
    
    # Apply stun mechanic
    stunned_units = state['stunned_units']
    for unit in stunned_units:
        if abs(unit[0] - r2) <= 1 and abs(unit[1] - c2) <= 1:
            stunned_units.remove(unit)
            break
    
    # Check if the center square is occupied
    if board[2][2] == 'B':
        return {'state': 'win', 'winner': 0}
    elif board[2][2] == 'R':
        return {'state': 'win', 'winner': 1}
    
    # Increment turn count
    state['turn_count'] += 1
    
    # Return the updated state
    return state

def get_current_player(state: State) -> int:
    return state['current_player']

def get_player_name(player_id: int) -> str:
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> List[float]:
    if state['state'] == 'win':
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    board = state['board']
    current_player = state['current_player']
    actions = []
    
    # Get positions of units for the current player
    units = [(r, c) for r, row in enumerate(board) for c, cell in enumerate(row) if cell == f'B{current_player}' or cell == f'R{1 - current_player}']
    
    for r, c in units:
        # Horizontal movements
        for dr, dc in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 5 and 0 <= nc < 5 and board[nr][nc] == ' ':
                actions.append(f'move ({r},{c}) to ({nr},{nc})')
        
        # Diagonal movements
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 5 and 0 <= nc < 5 and board[nr][nc] == ' ':
                actions.append(f'move ({r},{c}) to ({nr},{nc})')
    
    # Check if there are any stunned units
    stunned_units = state['stunned_units']
    for unit in units:
        if unit in stunned_units:
            stunned_units.remove(unit)
            actions.append(f'move ({unit[0]},{unit[1]}) to ({unit[0]},{unit[1]})')
    
    # Check if the current player has no legal moves
    if not actions:
        actions.append('pass')
    
    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    board = state['board']
    observations = []
    
    # Create observation for each player
    for player_id in range(2):
        obs = {'board': [], 'units': []}
        for r in range(5):
            for c in range(5):
                if board[r][c] == f'B{player_id}':
                    obs['units'].append((r, c))
                obs['board'].append(board[r][c])
        observations.append(obs)
    
    return observations