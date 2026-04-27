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
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    
    # Parse the action
    src, dest = action.split(' to ')
    src_row, src_col = map(int, src.split(','))
    dest_row, dest_col = map(int, dest.split(','))

    # Check if the source and destination are valid
    if not (0 <= src_row < 5 and 0 <= src_col < 5 and 0 <= dest_row < 5 and 0 <= dest_col < 5):
        raise ValueError("Invalid move")

    # Check if the source and destination squares are empty
    if state['board'][src_row][src_col] not in ('B', 'R') or state['board'][dest_row][dest_col] in ('B', 'R'):
        raise ValueError("Invalid move")

    # Check for stun condition
    stun_condition = False
    for stun_unit in state['stunned_units']:
        stun_src_row, stun_src_col = stun_unit['src_row'], stun_unit['src_col']
        stun_dest_row, stun_dest_col = stun_unit['dest_row'], stun_unit['dest_col']
        if abs(src_row - stun_src_row) + abs(src_col - stun_src_col) + abs(dest_row - stun_dest_row) + abs(dest_col - stun_dest_col) == 1:
            stun_condition = True
            break

    # Apply the move
    if not stun_condition:
        new_state['board'][src_row][src_col] = None
        new_state['board'][dest_row][dest_col] = state['board'][src_row][src_col]
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        new_state['turn_count'] += 1
    else:
        new_state['stunned_units'].append({
            'src_row': src_row,
            'src_col': src_col,
            'dest_row': dest_row,
            'dest_col': dest_col
        })
    
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
    legal_actions = []
    board = state['board']
    current_player = state['current_player']
    stunned_units = state['stunned_units']
    turn_count = state['turn_count']

    def is_valid_move(src_row, src_col, dest_row, dest_col):
        return 0 <= src_row < 5 and 0 <= src_col < 5 and 0 <= dest_row < 5 and 0 <= dest_col < 5 and board[src_row][src_col] in ('B', 'R') and board[dest_row][dest_col] is None

    def is_stun_condition(src_row, src_col, dest_row, dest_col):
        for stun_unit in stunned_units:
            stun_src_row, stun_src_col, stun_dest_row, stun_dest_col = stun_unit['src_row'], stun_unit['src_col'], stun_unit['dest_row'], stun_unit['dest_col']
            if abs(src_row - stun_src_row) + abs(src_col - stun_src_col) + abs(dest_row - stun_dest_row) + abs(dest_col - stun_dest_col) == 1:
                return True
        return False

    for row in range(5):
        for col in range(5):
            if board[row][col] is None:
                continue
            if board[row][col] == 'B':
                for dest_row, dest_col in [(row-1, col-1), (row-1, col), (row-1, col+1), (row, col-1), (row, col+1), (row+1, col-1), (row+1, col), (row+1, col+1)]:
                    if is_valid_move(row, col, dest_row, dest_col) and not is_stun_condition(row, col, dest_row, dest_col):
                        legal_actions.append(f'move ({row},{col}) to ({dest_row},{dest_col})')
            elif board[row][col] == 'R':
                for dest_row, dest_col in [(row-1, col-1), (row-1, col), (row-1, col+1), (row, col-1), (row, col+1), (row+1, col-1), (row+1, col), (row+1, col+1)]:
                    if is_valid_move(row, col, dest_row, dest_col) and not is_stun_condition(row, col, dest_row, dest_col):
                        legal_actions.append(f'move ({row},{col}) to ({dest_row},{dest_col})')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    current_player = state['current_player']
    observations = []

    def get_observation(player_id):
        observation = {}
        for row in range(5):
            for col in range(5):
                if board[row][col] is None:
                    observation[f'({row},{col})'] = None
                elif board[row][col] == 'B':
                    observation[f'({row},{col})'] = 'Blue'
                elif board[row][col] == 'R':
                    observation[f'({row},{col})'] = 'Red'
        observation['current_player'] = get_player_name(current_player)
        return observation

    observations.append(get_observation(0))
    observations.append(get_observation(1))
    return observations