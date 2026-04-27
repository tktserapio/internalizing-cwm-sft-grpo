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
        raise ValueError("Invalid action: Out of bounds")
    if board[sr][sc] != 'B' and board[sr][sc] != 'R':
        raise ValueError("Invalid action: Source square is empty")

    # Apply the action
    board[sr][sc], board[tr][tc] = None, 'B'
    if (sr + tr) % 2 == 0 and (sc + tc) % 2 == 0:
        board[tr][tc] = 'S'

    # Update the current player
    new_state['board'] = board
    new_state['current_player'] = 1 - current_player
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
    if state['current_player'] == -4:
        return [0.0, 0.0]
    return [1.0, 0.0] if state['board'][2][2] == 'B' else [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    board = state['board']
    current_player = state['current_player']
    legal_actions = []

    for sr, row in enumerate(board):
        for sc, cell in enumerate(row):
            if cell == 'B':
                for tr, row2 in enumerate(board):
                    for tc, cell2 in enumerate(row2):
                        if cell2 == None:
                            action = f"move ({sr},{sc}) to ({tr},{tc})"
                            if is_adjacent_to_opponent(cell, cell2, sr, sc, tr, tc):
                                legal_actions.append(action)
                            break

    return legal_actions

def is_adjacent_to_opponent(unit1: str, unit2: str, sr1: int, sc1: int, tr: int, tc: int) -> bool:
    """
    Helper function to check if the move is adjacent to the opponent's unit.
    """
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for dr, dc in directions:
        if (tr + dr, tc + dc) == (sr1, sc1):
            return True
    return False

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    player_0_obs = {
        'board': board,
        'current_player': get_current_player(state),
        'turn_count': state['turn_count']
    }
    player_1_obs = {
        'board': board,
        'current_player': get_current_player(state),
        'turn_count': state['turn_count']
    }
    return [player_0_obs, player_1_obs]