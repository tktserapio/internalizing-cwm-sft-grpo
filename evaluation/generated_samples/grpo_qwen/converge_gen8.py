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
            [None, None, 'C', None, None],
            [None, None, None, None, None],
            ['B', None, None, None, 'R']
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
    source_square = tuple(map(int, action.split()[1].split(',')))
    destination_square = tuple(map(int, action.split()[3].split(',')))

    # Check if the action is valid
    if source_square not in new_state['board'][player_id] or destination_square in new_state['board'][player_id]:
        raise ValueError("Invalid action")

    # Move the unit
    new_state['board'][player_id][source_square], new_state['board'][destination_square] = new_state['board'][destination_square], new_state['board'][source_square]

    # Apply stun mechanic
    for stun_square in new_state['stunned_units']:
        if abs(stun_square[0] - destination_square[0]) + abs(stun_square[1] - destination_square[1]) == 1:
            new_state['stunned_units'].append(destination_square)
            break

    # Update current player
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
    if state['current_player'] == 0 and state['board'][state['current_player']]['2,2'] == 'B':
        return [1.0, 0.0]
    elif state['current_player'] == 1 and state['board'][state['current_player']]['2,2'] == 'R':
        return [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_id = state['current_player']
    board = state['board'][player_id]
    current_player = get_player_name(player_id)

    legal_actions = []

    for square in board:
        if square is None:
            continue
        for adj_square in get_adjacent_squares(square):
            if adj_square not in board and adj_square not in state['stunned_units']:
                legal_actions.append(f'move ({square},{adj_square}) to ({adj_square}, {square})')
    
    if not legal_actions:
        return ['pass']
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {
        'board': state['board'][0],
        'current_player': state['current_player'],
        'turn_count': state['turn_count'],
        'stunned_units': state['stunned_units']
    }
    player_1_obs = {
        'board': state['board'][1],
        'current_player': state['current_player'],
        'turn_count': state['turn_count'],
        'stunned_units': state['stunned_units']
    }
    return [player_0_obs, player_1_obs]

def get_adjacent_squares(square: str) -> List[str]:
    """Returns a list of adjacent squares to the given square."""
    row, col = map(int, square.split(','))
    adjacent_squares = [
        f'{row-1},{col}',
        f'{row+1},{col}',
        f'{row},{col-1}',
        f'{row},{col+1}',
        f'{row-1},{col-1}',
        f'{row-1},{col+1}',
        f'{row+1},{col-1}',
        f'{row+1},{col+1}'
    ]
    return adjacent_squares