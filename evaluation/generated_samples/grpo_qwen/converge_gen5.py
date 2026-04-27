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
        raise ValueError("Invalid move")
    if board[sr][sc] != 'B' and board[sr][sc] != 'R':
        raise ValueError("Source square is not occupied")
    if board[tr][tc] is not None:
        raise ValueError("Target square is already occupied")

    # Apply the move
    board[sr][sc] = None
    board[tr][tc] = 'B' if current_player == 0 else 'R'

    # Update the current player
    new_state['current_player'] = 1 if current_player == 0 else 0

    # Update the turn count
    new_state['turn_count'] += 1

    # Check for stun condition
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if 0 <= tr + i < 5 and 0 <= tc + j < 5:
                if board[tr + i][tc + j] is not None and board[tr + i][tc + j] != 'B' and board[tr + i][tc + j] != 'R':
                    board[tr + i][tc + j] = 'S' if current_player == 0 else 'S'
                    break

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
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    legal_actions = []

    for sr, row in enumerate(board):
        for sc, piece in enumerate(row):
            if piece == 'B':
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    tr, tc = sr + dr, sc + dc
                    if 0 <= tr < 5 and 0 <= tc < 5 and board[tr][tc] is None:
                        legal_actions.append(f'move ({sr},{sc}) to ({tr},{tc})')
            elif piece == 'R':
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    tr, tc = sr + dr, sc + dc
                    if 0 <= tr < 5 and 0 <= tc < 5 and board[tr][tc] is None:
                        legal_actions.append(f'move ({sr},{sc}) to ({tr},{tc})')

    if not legal_actions:
        return ['pass']
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    current_player = state['current_player']

    player_0_obs = {
        'board': board,
        'current_player': current_player,
        'turn_count': state['turn_count']
    }
    player_1_obs = {
        'board': board,
        'current_player': current_player,
        'turn_count': state['turn_count']
    }

    return [player_0_obs, player_1_obs]