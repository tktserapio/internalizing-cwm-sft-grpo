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
        'board': [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
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
    new_state = {
        'board': [row[:] for row in state['board']],
        'positions': {0: state['positions'][0][:], 1: state['positions'][1][:]},
        'stunned': {0: state['stunned'][0][:], 1: state['stunned'][1][:]},
        'current_player': state['current_player'],
        'turn_count': state['turn_count'],
        'winner': state['winner']
    }

    if action.startswith("move"):
        move_action(new_state, action)
    elif action == "pass":
        pass_action(new_state)

    # Check for victory condition
    if CENTER_SQUARE in new_state['positions'][0]:
        new_state['winner'] = 0
    elif CENTER_SQUARE in new_state['positions'][1]:
        new_state['winner'] = 1

    # Increment turn count
    new_state['turn_count'] += 1

    # Switch current player
    new_state['current_player'] = 1 - new_state['current_player']

    return new_state

def move_action(state: State, action: Action):
    """Handles the move action and updates the state accordingly."""
    _, start, _, end = action.split()
    start = parse_position(start)
    end = parse_position(end)
    player = state['current_player']
    unit_index = state['positions'][player].index(start)
    
    # Move the unit
    state['positions'][player][unit_index] = end

    # Update stun status
    opponent = 1 - player
    for i, pos in enumerate(state['positions'][opponent]):
        if is_adjacent(end, pos):
            state['stunned'][opponent][i] = True

def pass_action(state: State):
    """Handles the pass action and updates the state accordingly."""
    # Clear stun status for the current player
    player = state['current_player']
    state['stunned'][player] = [False, False]

def parse_position(pos: str) -> Tuple[int, int]:
    """Parses a position string like '(r,c)' into a tuple (r, c)."""
    r, c = map(int, pos.strip('()').split(','))
    return r, c

def is_adjacent(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    """Checks if two positions are adjacent on the board."""
    return abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1

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
    if state['winner'] == 0:
        return [1.0, -1.0]
    elif state['winner'] == 1:
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
                if is_within_bounds(new_pos) and is_empty(state, new_pos):
                    legal_actions.append(f"move {pos} to {new_pos}")

    if not legal_actions:
        legal_actions.append("pass")

    return legal_actions

def is_within_bounds(pos: Tuple[int, int]) -> bool:
    """Checks if a position is within the board bounds."""
    return 0 <= pos[0] < BOARD_SIZE and 0 <= pos[1] < BOARD_SIZE

def is_empty(state: State, pos: Tuple[int, int]) -> bool:
    """Checks if a position is empty."""
    for positions in state['positions'].values():
        if pos in positions:
            return False
    return True

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]