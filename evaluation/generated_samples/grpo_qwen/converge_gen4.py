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
    """
    Returns the initial game state before any actions are taken.
    """
    return {
        'board': [
            ['B', None, None, None, 'R'],
            [None, None, None, None, None],
            [None, None, 'C', None, None],
            [None, None, None, None, None],
            ['B', None, None, None, 'R']
        ],
        'current_player': 0,
        'turn_count': 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    board = new_state['board']
    current_player = new_state['current_player']
    turn_count = new_state['turn_count']

    # Parse the action
    source, target = action.split(' to ')
    sr, sc = map(int, source.split(','))
    tr, tc = map(int, target.split(','))

    # Check if the action is valid
    if not (0 <= sr < 5 and 0 <= sc < 5 and 0 <= tr < 5 and 0 <= tc < 5):
        raise ValueError("Invalid action: Source or target out of bounds.")
    if board[sr][sc] is None or board[tr][tc] is not None:
        raise ValueError("Invalid action: Source or target is invalid.")

    # Apply the action
    board[sr][sc], board[tr][tc] = None, board[sr][sc]
    board[tr][tc] = 'P' if current_player == 0 else 'Q'

    # Update the current player
    new_state['board'] = board
    new_state['current_player'] = 1 if current_state['current_player'] == 0 else 0
    new_state['turn_count'] += 1

    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['current_player'] == 0 and state['board'][2][2] == 'P':
        return [1.0, 0.0]
    elif state['current_player'] == 1 and state['board'][2][2] == 'Q':
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    board = state['board']
    current_player = state['current_player']
    legal_actions = []

    for sr, row in enumerate(board):
        for sc, piece in enumerate(row):
            if piece is not None:
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, -1), (-1, 0)]:
                    tr, tc = sr + dr, sc + dc
                    if 0 <= tr < 5 and 0 <= tc < 5 and board[tr][tc] is None:
                        legal_actions.append(f'move ({sr},{sc}) to ({tr},{tc})')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    player_0_obs = {}
    player_1_obs = {}

    for sr, row in enumerate(board):
        for sc, piece in enumerate(row):
            if piece is not None:
                if piece == 'B':
                    player_0_obs[(sr, sc)] = 1
                elif piece == 'R':
                    player_1_obs[(sr, sc)] = 1
                elif piece == 'P':
                    player_0_obs[(sr, sc)] = 2
                elif piece == 'Q':
                    player_1_obs[(sr, sc)] = 2

    return [player_0_obs, player_1_obs]