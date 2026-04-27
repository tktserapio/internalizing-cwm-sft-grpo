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
    # Parse the action
    source, target = action.split(' to ')
    sr, sc = map(int, source.split(','))
    tr, tc = map(int, target.split(','))

    # Check if the action is valid
    if not (0 <= sr < 5 and 0 <= sc < 5 and 0 <= tr < 5 and 0 <= tc < 5):
        raise ValueError("Invalid move")
    
    # Get the source and target positions
    src_pos = (sr, sc)
    tgt_pos = (tr, tc)

    # Update the board
    new_state['board'][sr][sc] = None
    new_state['board'][tr][tc] = state['board'][sr][sc]

    # Apply movement logic
    if src_pos == tgt_pos:
        raise ValueError("Cannot move to the same position")

    # Check for stun condition
    for stun_pos in state['stunned_units']:
        if abs(src_pos[0] - stun_pos[0]) + abs(src_pos[1] - stun_pos[1]) == 1:
            new_state['stunned_units'].append(tgt_pos)
            break
    else:
        new_state['stunned_units'] = []

    # Update the current player
    new_state['current_player'] = (state['current_player'] + 1) % 2
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
    if state['current_player'] == 0 and state['board'][2][2] == 'B':
        return [1.0, 0.0]
    elif state['current_player'] == 1 and state['board'][2][2] == 'R':
        return [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    current_player = state['current_player']
    board = state['board']
    stunned_units = state['stunned_units']
    turn_count = state['turn_count']

    for row in range(5):
        for col in range(5):
            if board[row][col] == 'B' and (row, col) not in stunned_units:
                for dr, dc in [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 5 and 0 <= new_col < 5 and board[new_row][new_col] is None:
                        legal_actions.append(f'move ({row},{col}) to ({new_row},{new_col})')
            elif board[row][col] == 'R' and (row, col) not in stunned_units:
                for dr, dc in [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 5 and 0 <= new_col < 5 and board[new_row][new_col] is None:
                        legal_actions.append(f'move ({row},{col}) to ({new_row},{new_col})')

    if turn_count >= 50:
        return []

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []

    for player_id in [0, 1]:
        obs = {'board': [], 'stunned_units': []}
        for row in range(5):
            for col in range(5):
                if board[row][col] == 'B':
                    obs['board'].append((row, col))
                elif board[row][col] == 'R':
                    obs['board'].append((row, col))
                elif (row, col) in state['stunned_units']:
                    obs['stunned_units'].append((row, col))
        observations.append(obs)

    return observations