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

# Constants for the game
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
        'turn_count': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Copy the state to avoid mutation
    new_state = {
        'board': [row[:] for row in state['board']],
        'positions': {
            0: state['positions'][0][:],
            1: state['positions'][1][:]
        },
        'stunned': {
            0: state['stunned'][0][:],
            1: state['stunned'][1][:]
        },
        'current_player': state['current_player'],
        'turn_count': state['turn_count'],
        'winner': state['winner']
    }

    if action.startswith("move"):
        # Parse the action
        parts = action.split()
        r1, c1 = map(int, parts[1][1:-1].split(','))
        r2, c2 = map(int, parts[3][1:-1].split(','))

        # Find the index of the moving unit
        player = new_state['current_player']
        unit_index = new_state['positions'][player].index((r1, c1))

        # Move the unit
        new_state['positions'][player][unit_index] = (r2, c2)

        # Check for victory
        if (r2, c2) == CENTER_SQUARE:
            new_state['winner'] = player

        # Update stun status for opponent
        opponent = 1 - player
        for i, (orow, ocol) in enumerate(new_state['positions'][opponent]):
            if abs(orow - r2) <= 1 and abs(ocol - c2) <= 1:
                new_state['stunned'][opponent][i] = True

    # Update current player and turn count
    new_state['current_player'] = 1 - new_state['current_player']
    new_state['turn_count'] += 1

    # Reset stun status for the current player
    for i in range(len(new_state['stunned'][new_state['current_player']])):
        new_state['stunned'][new_state['current_player']][i] = False

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['winner'] is not None or state['turn_count'] >= MAX_TURNS:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Blue" if player_id == 0 else "Red"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['winner'] is not None:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    if state['turn_count'] >= MAX_TURNS:
        return [0.5, 0.5]  # Draw
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['winner'] is not None or state['turn_count'] >= MAX_TURNS:
        return []

    legal_actions = []
    player = state['current_player']
    for i, (r, c) in enumerate(state['positions'][player]):
        if state['stunned'][player][i]:
            continue
        # Check all adjacent squares
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if (nr, nc) not in state['positions'][0] and (nr, nc) not in state['positions'][1]:
                        legal_actions.append(f"move ({r},{c}) to ({nr},{nc})")

    if not legal_actions:
        legal_actions.append("pass")

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]