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
    player_id = new_state['current_player']
    board = new_state['board']
    stunned_units = new_state['stunned_units']
    
    # Parse the action
    source, target = action.split(' to ')
    sr, sc = map(int, source.split(','))
    tr, tc = map(int, target.split(','))

    # Check if the action is valid
    if not (0 <= sr < 5 and 0 <= sc < 5 and 0 <= tr < 5 and 0 <= tc < 5):
        raise ValueError("Invalid move")
    if board[sr][sc] != 'B' and board[sr][sc] != 'R':
        raise ValueError("Source square is not occupied")
    if board[tr][tc] is not None:
        raise ValueError("Target square is occupied")

    # Apply the move
    board[sr][sc], board[tr][tc] = None, 'B'
    if board[sr][sc] == 'B':
        stunned_units.append((sr, sc))
    if board[tr][tc] == 'B':
        stunned_units.append((tr, tc))

    # Update the current player
    new_state['current_player'] = 1 if player_id == 0 else 0
    new_state['turn_count'] += 1
    
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
        return [0.0, 0.0]
    return [1.0, 0.0] if state['board'][2][2] == 'B' else [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    stunned_units = state['stunned_units']
    legal_actions = []

    for sr, sc in [(r, c) for r in range(5) for c in range(5) if board[r][c] == 'B']:
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            tr, tc = sr + dr, sc + dc
            if 0 <= tr < 5 and 0 <= tc < 5 and board[tr][tc] is None:
                legal_actions.append(f'move ({sr},{sc}) to ({tr},{tc})')
            elif 0 <= tr < 5 and 0 <= tc < 5 and board[tr][tc] == 'R' and (tr, tc) not in stunned_units:
                legal_actions.append(f'move ({sr},{sc}) to ({tr},{tc})')

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    player_0_obs = {'board': board, 'current_player': state['current_player']}
    player_1_obs = {'board': board, 'current_player': state['current_player']}
    return [player_0_obs, player_1_obs]