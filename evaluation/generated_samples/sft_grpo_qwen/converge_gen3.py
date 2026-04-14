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
        'turn': 0,
        'stun': {}
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = get_current_player(new_state)
    if action == 'pass':
        new_state['turn'] += 1
        return new_state
    
    # Parse the action
    source, target = action.split(' to ')
    sr, sc = map(int, source.split(','))
    tr, tc = map(int, target.split(','))
    
    # Check if the action is valid
    if (sr, sc) not in new_state['board']:
        raise ValueError(f"Invalid source position {source}")
    if (tr, tc) not in new_state['board']:
        raise ValueError(f"Invalid target position {target}")
    if new_state['board'][sr, sc]['player'] != player_id:
        raise ValueError("Cannot move another player's unit")
    
    # Apply the move
    new_state['board'][tr, tc]['player'] = player_id
    new_state['board'][sr, sc]['player'] = None
    
    # Handle stun
    if (sr, sc) in new_state['stun']:
        new_state['stun'][sr, sc]['status'] = False
        del new_state['stun'][sr, sc]
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['turn'] % 2 == 0:
        return 0
    else:
        return 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['board'][2, 2]['player'] == 0:
        return [1.0, 0.0]
    elif state['board'][2, 2]['player'] == 1:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_id = get_current_player(state)
    legal_actions = []
    
    for pos, player in state['board'].items():
        if player['player'] == player_id:
            for dr, dc in [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]:
                new_pos = (pos[0] + dr, pos[1] + dc)
                if new_pos in state['board'] and state['board'][new_pos]['player'] is None:
                    legal_actions.append(f'move {pos} to {new_pos}')
    
    # Add pass action if no legal moves
    if not legal_actions:
        legal_actions.append('pass')
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {
        'board': state['board'],
        'turn': state['turn'],
        'stun': state['stun']
    }
    player_1_obs = {
        'board': state['board'],
        'turn': state['turn'],
        'stun': state['stun']
    }
    return [player_0_obs, player_1_obs]