import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
BOARD_SIZE = 5
CENTER_SQUARE = (2, 2)
MAX_TURNS = 50

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None]
        ],
        'positions': {
            0: [(0, 0), (0, 4)],
            1: [(4, 0), (4, 4)]
        },
        'stunned': {
            0: [False, False],
            1: [False, False]
        },
        'current_player': 0,
        'turn_count': 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        'board': [row[:] for row in state['board']],
        'positions': {k: v[:] for k, v in state['positions'].items()},
        'stunned': {k: v[:] for k, v in state['stunned'].items()},
        'current_player': state['current_player'],
        'turn_count': state['turn_count']
    }

    if action.startswith("move"):
        # Parse the action string
        parts = action.split()
        start_pos = tuple(map(int, parts[1][1:-1].split(',')))
        end_pos = tuple(map(int, parts[3][1:-1].split(',')))

        # Find which unit is moving
        player = new_state['current_player']
        unit_index = new_state['positions'][player].index(start_pos)

        # Update the position of the moving unit
        new_state['positions'][player][unit_index] = end_pos

        # Check for stunning adjacent opponent units
        opponent = 1 - player
        for i, pos in enumerate(new_state['positions'][opponent]):
            if is_adjacent(end_pos, pos):
                new_state['stunned'][opponent][i] = True

    # Update the current player and turn count
    new_state['current_player'] = 1 - new_state['current_player']
    new_state['turn_count'] += 1

    # Clear stun status for the current player's units
    for i in range(len(new_state['stunned'][new_state['current_player']])):
        new_state['stunned'][new_state['current_player']][i] = False

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['turn_count'] >= MAX_TURNS or CENTER_SQUARE in state['positions'][0] or CENTER_SQUARE in state['positions'][1]:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Blue" if player_id == 0 else "Red"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if CENTER_SQUARE in state['positions'][0]:
        return [1.0, -1.0]
    elif CENTER_SQUARE in state['positions'][1]:
        return [-1.0, 1.0]
    elif state['turn_count'] >= MAX_TURNS:
        return [0.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if get_current_player(state) == -4:
        return []

    player = state['current_player']
    legal_actions = []

    for i, pos in enumerate(state['positions'][player]):
        if state['stunned'][player][i]:
            continue

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_pos = (pos[0] + dr, pos[1] + dc)
                if is_within_bounds(new_pos) and new_pos not in state['positions'][0] and new_pos not in state['positions'][1]:
                    legal_actions.append(f"move {pos} to {new_pos}")

    if not legal_actions:
        legal_actions.append("pass")

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

def is_adjacent(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    """Check if two positions are adjacent."""
    return abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1

def is_within_bounds(pos: Tuple[int, int]) -> bool:
    """Check if a position is within the board bounds."""
    return 0 <= pos[0] < BOARD_SIZE and 0 <= pos[1] < BOARD_SIZE