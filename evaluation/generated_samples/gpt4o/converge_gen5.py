import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Dict, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'units': {
            0: [(0, 0), (0, 4)],  # Player 0's units
            1: [(4, 0), (4, 4)]   # Player 1's units
        },
        'stunned': {
            0: [False, False],    # Stun status for Player 0's units
            1: [False, False]     # Stun status for Player 1's units
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
        'units': {0: state['units'][0][:], 1: state['units'][1][:]},
        'stunned': {0: state['stunned'][0][:], 1: state['stunned'][1][:]},
        'current_player': state['current_player'],
        'turn_count': state['turn_count'],
        'winner': state['winner']
    }

    if action == "pass":
        # Simply switch players and increment turn count
        new_state['current_player'] = 1 - state['current_player']
        new_state['turn_count'] += 1
        return new_state

    # Parse the action string
    parts = action.split()
    r1, c1 = map(int, parts[1][1:-1].split(','))
    r2, c2 = map(int, parts[3][1:-1].split(','))

    # Determine which unit is moving
    player = state['current_player']
    unit_index = new_state['units'][player].index((r1, c1))

    # Move the unit
    new_state['units'][player][unit_index] = (r2, c2)

    # Check for victory condition
    if (r2, c2) == (2, 2):
        new_state['winner'] = player
        return new_state

    # Update stun status
    opponent = 1 - player
    for i, (orow, ocol) in enumerate(new_state['units'][opponent]):
        if abs(orow - r2) <= 1 and abs(ocol - c2) <= 1:
            new_state['stunned'][opponent][i] = True
        else:
            new_state['stunned'][opponent][i] = False

    # Switch players and increment turn count
    new_state['current_player'] = opponent
    new_state['turn_count'] += 1

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['winner'] is not None or state['turn_count'] >= 50:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Blue" if player_id == 0 else "Red"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['winner'] is not None:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    if state['turn_count'] >= 50:
        return [0.5, 0.5]  # Draw
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['winner'] is not None or state['turn_count'] >= 50:
        return []

    player = state['current_player']
    legal_actions = []
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for i, (r, c) in enumerate(state['units'][player]):
        if state['stunned'][player][i]:
            continue  # Skip stunned units

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 5 and 0 <= nc < 5 and (nr, nc) not in state['units'][0] and (nr, nc) not in state['units'][1]:
                legal_actions.append(f"move ({r},{c}) to ({nr},{nc})")

    if not legal_actions:
        legal_actions.append("pass")

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]