import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to create an initial state
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [
            ['B', None, None, None, 'R'],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            ['R', None, None, None, 'B']
        ],
        'current_player': 0,
        'turn_count': 0,
        'stunned_units': []
    }

# Apply action to the state
def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        new_state['turn_count'] += 1
        return new_state
    
    # Parse the action
    source, target = action.split(' to ')
    sr, sc = map(int, source.split(','))
    tr, tc = map(int, target.split(','))
    
    # Check if the action is valid
    if not (0 <= sr < 5 and 0 <= sc < 5 and 0 <= tr < 5 and 0 <= tc < 5):
        raise ValueError("Invalid move")
    
    # Update board
    new_board = [[state['board'][i][j] for j in range(5)] for i in range(5)]
    new_board[sr][sc], new_board[tr][tc] = None, state['board'][sr][sc]
    
    # Check for stun
    for stun in state['stunned_units']:
        if abs(stun[0] - tr) + abs(stun[1] - tc) == 1:
            new_board[stun[0]][stun[1]] = None
            state['stunned_units'].remove(stun)
    
    new_state['board'] = new_board
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    new_state['turn_count'] += 1
    
    return new_state

# Get current player
def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

# Get player name
def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

# Get rewards
def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['current_player'] == 0 and state['board'][2][2] == 'B':
        return [1.0, 0.0]
    elif state['current_player'] == 1 and state['board'][2][2] == 'R':
        return [0.0, 1.0]
    return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for r in range(5):
        for c in range(5):
            if state['board'][r][c] == 'B':
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, 0), (-1, -1), (0, -1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 5 and 0 <= nc < 5 and state['board'][nr][nc] is None:
                        legal_actions.append(f'move ({r},{c}) to ({nr},{nc})')
            elif state['board'][r][c] == 'R':
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, 0), (-1, -1), (0, -1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 5 and 0 <= nc < 5 and state['board'][nr][nc] is None:
                        legal_actions.append(f'move ({r},{c}) to ({nr},{nc})')
    return legal_actions

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {
        'board': state['board'],
        'current_player': state['current_player'],
        'turn_count': state['turn_count'],
        'stunned_units': state['stunned_units']
    }
    player_1_obs = {
        'board': state['board'],
        'current_player': state['current_player'],
        'turn_count': state['turn_count'],
        'stunned_units': state['stunned_units']
    }
    return [player_0_obs, player_1_obs]