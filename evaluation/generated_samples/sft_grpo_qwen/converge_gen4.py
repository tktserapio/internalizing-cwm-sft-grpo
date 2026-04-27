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

# Helper function to initialize the state
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    return {
        'board': [
            ['B', None, None, None, 'R'],
            [None, None, None, None, None],
            [None, None, 'B', None, None],
            [None, None, None, None, None],
            ['R', None, None, None, 'B']
        ],
        'current_player': 0,
        'turn_count': 0,
        'stunned_units': []
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    else:
        # Parse the action
        source, target = action.split(' to ')
        sr, sc = map(int, source.split(','))
        tr, tc = map(int, target.split(','))

        # Check if the action is valid
        if not (0 <= sr < 5 and 0 <= sc < 5 and 0 <= tr < 5 and 0 <= tc < 5):
            raise ValueError("Invalid move: out of board bounds")
        if state['board'][sr][sc] != 'B' and state['board'][sr][sc] != 'R':
            raise ValueError("Invalid move: source square is empty")
        if state['board'][tr][tc] != None:
            raise ValueError("Invalid move: target square is occupied")

        # Update the board
        new_state['board'][sr][sc] = None
        new_state['board'][tr][tc] = 'B' if state['current_player'] == 0 else 'R'

        # Handle stun mechanic
        for x, y in [(sr-1, sc), (sr+1, sc), (sr, sc-1), (sr, sc+1), (sr-1, sc-1), (sr-1, sc+1), (sr+1, sc-1), (sr+1, sc+1)]:
            if 0 <= x < 5 and 0 <= y < 5 and state['board'][x][y] == 'R' if state['current_player'] == 0 else 'B':
                new_state['stunned_units'].append((x, y))
                break

        # Remove stunned units after their turn
        new_state['stunned_units'] = [unit for unit in new_state['stunned_units'] if new_state['turn_count'] % 2 != 0]

        # Update current player
        new_state['current_player'] = (new_state['current_player'] + 1) % 2

        # Increment turn count
        new_state['turn_count'] += 1

        return new_state

# Get the current player
def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Blue' if player_id == 0 else 'Red'

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['current_player'] == -4:
        return [0.0, 0.0]
    else:
        return [1.0, 0.0] if state['board'][2][2] == 'B' else [0.0, 1.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    for sr, sc in [(i, j) for i in range(5) for j in range(5) if state['board'][i][j] == 'B']:
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            tr, tc = sr + dr, sc + dc
            if 0 <= tr < 5 and 0 <= tc < 5 and state['board'][tr][tc] is None:
                legal_actions.append(f'move ({sr},{sc}) to ({tr},{tc})')
    return legal_actions

# Get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {'board': state['board'], 'current_player': state['current_player']}
    player_1_obs = {'board': state['board'], 'current_player': state['current_player']}
    return [player_0_obs, player_1_obs]