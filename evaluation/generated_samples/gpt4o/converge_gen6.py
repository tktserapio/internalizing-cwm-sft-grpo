import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [
            [0, None, None, None, 0],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [1, None, None, None, 1]
        ],
        'current_player': 0,
        'stunned_units': {0: [], 1: []},
        'turns': 0
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = {
        'board': [row[:] for row in state['board']],
        'current_player': state['current_player'],
        'stunned_units': {0: state['stunned_units'][0][:], 1: state['stunned_units'][1][:]},
        'turns': state['turns'] + 1
    }
    
    if action == "pass":
        new_state['current_player'] = 1 - state['current_player']
        return new_state
    
    # Parse the action
    _, start, _, end = action.split()
    r1, c1 = map(int, start.strip('()').split(','))
    r2, c2 = map(int, end.strip('()').split(','))
    
    # Move the unit
    player = state['current_player']
    new_state['board'][r1][c1] = None
    new_state['board'][r2][c2] = player
    
    # Update stunned units
    opponent = 1 - player
    new_state['stunned_units'][opponent] = [
        (r, c) for r, c in new_state['stunned_units'][opponent] if (r, c) != (r2, c2)
    ]
    
    # Check for new stuns
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r2 + dr, c2 + dc
            if 0 <= nr < 5 and 0 <= nc < 5 and new_state['board'][nr][nc] == opponent:
                new_state['stunned_units'][opponent].append((nr, nc))
    
    # Switch player
    new_state['current_player'] = opponent
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['board'][2][2] is not None:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Blue" if player_id == 0 else "Red"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['board'][2][2] == 0:
        return [1.0, -1.0]
    elif state['board'][2][2] == 1:
        return [-1.0, 1.0]
    elif state['turns'] >= 50:
        return [0.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if get_current_player(state) == -4:
        return []
    
    player = state['current_player']
    legal_actions = []
    
    # Find all units of the current player
    units = [(r, c) for r in range(5) for c in range(5) if state['board'][r][c] == player]
    
    for r, c in units:
        if (r, c) in state['stunned_units'][player]:
            continue
        # Check all possible moves
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 5 and 0 <= nc < 5 and state['board'][nr][nc] is None:
                    legal_actions.append(f"move ({r},{c}) to ({nr},{nc})")
    
    if not legal_actions:
        legal_actions.append("pass")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]