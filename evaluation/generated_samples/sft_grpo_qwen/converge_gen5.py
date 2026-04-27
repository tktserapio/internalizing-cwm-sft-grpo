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
        'board': {
            (0, 0): {'player': 0},
            (0, 4): {'player': 0},
            (1, 0): {'player': None},
            (1, 4): {'player': None},
            (2, 0): {'player': None},
            (2, 1): {'player': None},
            (2, 2): {'player': None},
            (2, 3): {'player': None},
            (2, 4): {'player': None},
            (3, 0): {'player': None},
            (3, 4): {'player': None},
            (4, 0): {'player': 1},
            (4, 1): {'player': None},
            (4, 2): {'player': None},
            (4, 3): {'player': None},
            (4, 4): {'player': 1}
        },
        'current_player': 0,
        'turn_count': 0,
        'stunned_units': []
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken. Ensure the previous state is not mutated; always return a new state object."""
    new_state = state.copy()
    new_state['turn_count'] += 1
    
    # Parse the action
    source, target = action.split(' to ')
    source = tuple(map(int, source.split(',')))
    target = tuple(map(int, target.split(',')))
    
    # Check if the action is valid
    if source not in new_state['board']:
        raise ValueError(f"Invalid source position {source}")
    if target in new_state['board']:
        raise ValueError(f"Target position {target} is already occupied")
    
    # Apply the move
    new_state['board'][target] = new_state['board'].pop(source)
    new_state['board'][target]['player'] = new_state['current_player']
    
    # Check for stun
    for pos, unit in new_state['board'].items():
        if unit['player'] == new_state['current_player']:
            if abs(pos[0] - target[0]) + abs(pos[1] - target[1]) == 1:
                new_state['stunned_units'].append(pos)
    
    # Update current player
    new_state['current_player'] = 1 if new_state['current_player'] == 0 else 0
    
    # Check for win condition
    if target == (2, 2):
        new_state['stunned_units'] = []  # Clear stun after winning
        new_state['current_player'] = -4  # Terminal state
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['current_player'] == -4:
        return [1.0, 1.0]  # Both players win
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    board = state['board']
    current_player = state['current_player']
    
    for pos, unit in board.items():
        if unit['player'] == current_player:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                next_pos = (pos[0] + dx, pos[1] + dy)
                if next_pos in board and board[next_pos]['player'] is None:
                    legal_actions.append(f"move {pos} to {next_pos}")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = [
        {
            'board': {k: v['player'] for k, v in board.items()},
            'current_player': state['current_player'],
            'turn_count': state['turn_count'],
            'stunned_units': state['stunned_units']
        },
        {
            'board': {k: v['player'] for k, v in board.items()},
            'current_player': state['current_player'],
            'turn_count': state['turn_count'],
            'stunned_units': state['stunned_units']
        }
    ]
    return observations