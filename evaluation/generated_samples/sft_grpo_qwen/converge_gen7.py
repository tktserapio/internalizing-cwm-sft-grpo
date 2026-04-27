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
    player_id = new_state['current_player']
    board = new_state['board']
    turn_count = new_state['turn_count']

    # Parse the action
    src_row, src_col = map(int, action.split(' to ')[0].split(','))
    dest_row, dest_col = map(int, action.split(' to ')[1].split(','))

    # Check if the action is valid
    if board[src_row][src_col] != 'B' and board[src_row][src_col] != 'R':
        raise ValueError("Invalid source position")
    if board[dest_row][dest_col] is not None:
        raise ValueError("Destination position is occupied")

    # Apply the action
    board[src_row][src_col], board[dest_row][dest_col] = None, 'B'
    new_state['board'] = board

    # Update current player
    new_state['current_player'] = 1 if player_id == 0 else 0

    # Update turn count
    new_state['turn_count'] += 1

    # Check for stun
    for row in range(5):
        for col in range(5):
            if board[row][col] == 'R' and abs(row - src_row) + abs(col - src_col) == 1:
                board[row][col] = 'S'
                new_state['board'] = board
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
    if state['current_player'] == -4:
        return [0.0, 0.0]
    return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_id = state['current_player']
    board = state['board']
    legal_actions = []

    for row in range(5):
        for col in range(5):
            if board[row][col] == 'B':
                for dr, dc in [(0, 1), (1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1), (-1, 0), (0, -1)]:
                    dest_row, dest_col = row + dr, col + dc
                    if 0 <= dest_row < 5 and 0 <= dest_col < 5 and board[dest_row][dest_col] is None:
                        legal_actions.append(f'move ({row},{col}) to ({dest_row},{dest_col})')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    player_0_obs = {'board': board, 'current_player': state['current_player']}
    player_1_obs = {'board': board, 'current_player': state['current_player']}
    return [player_0_obs, player_1_obs]