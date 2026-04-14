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

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    r1, c1 = map(int, action.split(' ')[1][1:-1].split(','))
    r2, c2 = map(int, action.split(' ')[3][1:-1].split(','))

    # Check if the action is valid
    if not (0 <= r1 < 5 and 0 <= c1 < 5 and 0 <= r2 < 5 and 0 <= c2 < 5):
        raise ValueError("Invalid move coordinates")
    
    # Apply the move
    new_state['board'][r1][c1] = None
    new_state['board'][r2][c2] = state['board'][r1][c1]
    new_state['board'][r1][c1] = None
    
    # Update the current player
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    # Check for stun
    for i in range(5):
        for j in range(5):
            if new_state['board'][i][j] == state['board'][r1][c1]:
                new_state['stunned_units'].append((i, j))
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['current_player'] == 0 and state['board'][2][2] == 'B':
        return [1.0, 0.0]
    elif state['current_player'] == 1 and state['board'][2][2] == 'R':
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    board = state['board']
    current_player = state['current_player']
    
    # Get all units for the current player
    units = [(i, j) for i in range(5) for j in range(5) if board[i][j] == ('B' if current_player == 0 else 'R')]
    
    for unit in units:
        r, c = unit
        # Check horizontal movements
        if c > 0 and board[r][c-1] is None:
            legal_actions.append(f"move ({r},{c}) to ({r},{c-1})")
        if c < 4 and board[r][c+1] is None:
            legal_actions.append(f"move ({r},{c}) to ({r},{c+1})")
        
        # Check vertical movements
        if r > 0 and board[r-1][c] is None:
            legal_actions.append(f"move ({r},{c}) to ({r-1},{c})")
        if r < 4 and board[r+1][c] is None:
            legal_actions.append(f"move ({r},{c}) to ({r+1},{c})")
        
        # Check diagonal movements
        if r > 0 and c > 0 and board[r-1][c-1] is None:
            legal_actions.append(f"move ({r},{c}) to ({r-1},{c-1})")
        if r > 0 and c < 4 and board[r-1][c+1] is None:
            legal_actions.append(f"move ({r},{c}) to ({r-1},{c+1})")
        if r < 4 and c > 0 and board[r+1][c-1] is None:
            legal_actions.append(f"move ({r},{c}) to ({r+1},{c-1})")
        if r < 4 and c < 4 and board[r+1][c+1] is None:
            legal_actions.append(f"move ({r},{c}) to ({r+1},{c+1})")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []
    
    # Player 0 observation
    player_0_obs = {
        'board': board,
        'current_player': get_current_player(state),
        'turn_count': state['turn_count'],
        'stunned_units': state['stunned_units']
    }
    
    # Player 1 observation
    player_1_obs = {
        'board': board,
        'current_player': get_current_player(state),
        'turn_count': state['turn_count'],
        'stunned_units': state['stunned_units']
    }
    
    observations = [player_0_obs, player_1_obs]
    
    return observations