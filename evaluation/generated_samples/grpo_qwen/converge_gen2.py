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

# Helper function to parse the action string
def parse_action(action_str: Action) -> Tuple[int, int, int, int]:
    """Parses the action string into source and destination coordinates."""
    parts = action_str.split(' to ')
    src = tuple(map(int, parts[0].split(',')))
    dst = tuple(map(int, parts[1].split(',')))
    return src, dst

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for Blue (Player 0) and Red (Player 1)
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
    """Returns the new state after an action has been taken."""
    src, dst = parse_action(action)
    new_state = state.copy()
    
    # Check if the action is a valid move
    if not (0 <= src[0] < 5 and 0 <= src[1] < 5 and 0 <= dst[0] < 5 and 0 <= dst[1] < 5):
        raise ValueError("Invalid move coordinates")
    
    # Check if the destination is already occupied
    if (dst[0], dst[1]) in new_state['blue_units'] + new_state['red_units']:
        raise ValueError("Destination is occupied")
    
    # Apply the move
    if src == dst:
        new_state['center_square_occupied'] = True
    else:
        new_state['blue_units'].append(dst) if new_state['current_player'] == 0 else new_state['red_units'].append(dst)
        new_state['blue_units'].remove(src) if new_state['current_player'] == 0 else new_state['red_units'].remove(src)
    
    # Update the turn count
    new_state['turn_count'] += 1
    
    # Check for stun condition
    if (new_state['blue_units'] + new_state['red_units']) and \
       any(abs(src[0] - d[0]) <= 1 and abs(src[1] - d[1]) <= 1 for src in new_state['blue_units'] for d in new_state['red_units']):
        new_state['current_player'] = 1 - new_state['current_player']
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['center_square_occupied']:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['center_square_occupied']:
        return [-1.0, 1.0] if state['current_player'] == 0 else [1.0, -1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    if state['current_player'] == 0:
        for src in state['blue_units']:
            for dst in [(src[0]+1, src[1]), (src[0]-1, src[1]), (src[0], src[1]+1), (src[0], src[1]-1), (src[0]+1, src[1]+1), (src[0]+1, src[1]-1), (src[0]-1, src[1]+1), (src[0]-1, src[1]-1)]:
                if 0 <= dst[0] < 5 and 0 <= dst[1] < 5 and dst not in state['blue_units'] + state['red_units']:
                    legal_actions.append(f'move {src} to {dst}')
    else:
        for src in state['red_units']:
            for dst in [(src[0]+1, src[1]), (src[0]-1, src[1]), (src[0], src[1]+1), (src[0], src[1]-1), (src[0]+1, src[1]+1), (src[0]+1, src[1]-1), (src[0]-1, src[1]+1), (src[0]-1, src[1]-1)]:
                if 0 <= dst[0] < 5 and 0 <= dst[1] < 5 and dst not in state['blue_units'] + state['red_units']:
                    legal_actions.append(f'move {src} to {dst}')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    obs_0 = {'units': state['blue_units']}
    obs_1 = {'units': state['red_units']}
    return [obs_0, obs_1]