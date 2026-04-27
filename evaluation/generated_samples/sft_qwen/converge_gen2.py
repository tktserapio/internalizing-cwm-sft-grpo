import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def is_valid_move(action: Action, state: State) -> bool:
    """Check if the given action is valid based on the current state."""
    # Extract coordinates from the action string
    start, end = action.split(' to ')
    start_row, start_col = map(int, start.split(','))
    end_row, end_col = map(int, end.split(','))

    # Check if the start and end positions are within the board boundaries
    if not (0 <= start_row < 5 and 0 <= start_col < 5 and 0 <= end_row < 5 and 0 <= end_col < 5):
        return False

    # Check if the destination is empty
    if (end_row, end_col) in state['occupied']:
        return False

    return True

def is_adjacent(start: tuple[int, int], end: tuple[int, int]) -> bool:
    """Check if two positions are adjacent orthogonally or diagonally."""
    return abs(start[0] - end[0]) + abs(start[1] - end[1]) == 1

def get_center_square() -> tuple[int, int]:
    """Return the coordinates of the center square."""
    return (2, 2)

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    state = {
        'occupied': {
            (0, 0): 0,
            (0, 4): 0,
            (4, 0): 1,
            (4, 4): 1
        },
        'turn': 0,
        'stunned': {},
        'center_square': get_center_square()
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = copy.deepcopy(state)
    start, end = action.split(' to ')
    start_row, start_col = map(int, start.split(','))
    end_row, end_col = map(int, end.split(','))

    # Apply the move
    if is_valid_move(action, state):
        new_state['occupied'][end] = new_state['occupied'].pop((start_row, start_col))
        new_state['occupied'][end] = new_state['turn']
        new_state['occupied'].setdefault((end_row, end_col), 0)
        new_state['occupied'][(end_row, end_col)] += 1

        # Check for stun effect
        for key, value in new_state['occupied'].items():
            if value == 1 and is_adjacent(key, (end_row, end_col)):
                new_state['stunned'][key] = new_state['turn']

        # Update turn
        new_state['turn'] = (new_state['turn'] + 1) % 2

        # Check if the center square was reached
        if (end_row, end_col) == new_state['center_square']:
            return {'terminal': True, 'winner': new_state['turn']}
        
        # Check if it's a pass
        if action == 'pass':
            return {'terminal': True, 'winner': None}

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['turn']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['terminal']:
        if state['winner'] is None:
            return [0.0, 0.0]
        elif state['winner'] == 0:
            return [1.0, 0.0]
        else:
            return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_moves = []
    for pos, player in state['occupied'].items():
        if player == state['turn']:
            for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, -1)]:
                new_pos = (pos[0] + dr, pos[1] + dc)
                if is_valid_move(f'move {pos} to {new_pos}', state):
                    legal_moves.append(f'move {pos} to {new_pos}')
            if len(legal_moves) == 0:
                legal_moves.append('pass')
    return legal_moves

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {}
    player_1_obs = {}

    # Player 0 sees only its own units
    for pos, player in state['occupied'].items():
        if player == 0:
            player_0_obs[pos] = state['occupied'][pos]

    # Player 1 sees only its own units
    for pos, player in state['occupied'].items():
        if player == 1:
            player_1_obs[pos] = state['occupied'][pos]

    return [player_0_obs, player_1_obs]