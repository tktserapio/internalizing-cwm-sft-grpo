import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for players
    initial_positions = {
        'p0': {'row': random.randint(0, 1), 'col': random.randint(0, 1)},
        'p1': {'row': random.randint(2, 3), 'col': random.randint(2, 3)}
    }
    # Observations for players
    observations = [
        {'my_loc': f"({initial_positions['p0']['row']}, {initial_positions['p0']['col']}), Quadrant: Top-Left", 'opp_quadrant': 'Bottom-Right'},
        {'my_loc': f"({initial_positions['p1']['row']}, {initial_positions['p1']['col']}), Quadrant: Bottom-Right", 'opp_quadrant': 'Top-Left'}
    ]
    return {
        'state': 'setup',
        'positions': initial_positions,
        'observations': observations
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    if state['state'] == 'setup':
        new_state['state'] = 'movement'
        new_state['positions']['p0']['row'], new_state['positions']['p0']['col'] = state['positions']['p0']['row'], state['positions']['p0']['col']
        new_state['positions']['p1']['row'], new_state['positions']['p1']['col'] = state['positions']['p1']['row'], state['positions']['p1']['col']
    else:
        player_id = 'p0' if action.startswith('place_p0') else 'p1'
        opponent_id = 'p1' if action.startswith('place_p0') else 'p0'
        new_state['positions'][player_id]['row'], new_state['positions'][player_id]['col'] = parse_position(action[action.find(':') + 1:])
        new_state['positions'][opponent_id]['row'], new_state['positions'][opponent_id]['col'] = parse_position(state['positions'][opponent_id]['loc'])
    new_state['observations'][0]['my_loc'] = f"({new_state['positions']['p0']['row']}, {new_state['positions']['p0']['col']}), Quadrant: {get_quadrant(new_state['positions']['p0'])}"
    new_state['observations'][1]['my_loc'] = f"({new_state['positions']['p1']['row']}, {new_state['positions']['p1']['col']}), Quadrant: {get_quadrant(new_state['positions']['p1'])}"
    return new_state

def parse_position(position: str) -> tuple[int, int]:
    """Parses the row and column from the position string."""
    row, col = map(int, position.split(','))
    return row, col

def get_quadrant(position: dict[str, Any]) -> str:
    """Determines the quadrant based on the position."""
    row, col = position['row'], position['col']
    if row < 2 and col < 2:
        return 'Top-Left'
    elif row < 2 and col > 1:
        return 'Top-Right'
    elif row > 1 and col < 2:
        return 'Bottom-Left'
    else:
        return 'Bottom-Right'

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['state'] == 'setup':
        return -4
    else:
        return 0 if state['positions']['p0']['row'] == state['positions']['p1']['row'] and state['positions']['p0']['col'] == state['positions']['p1']['col'] else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['state'] == 'setup':
        return [0.0, 0.0]
    else:
        p0_loc = state['positions']['p0']['row'], state['positions']['p0']['col']
        p1_loc = state['positions']['p1']['row'], state['positions']['p1']['col']
        if p0_loc == p1_loc:
            return [-1.0, 1.0]
        else:
            return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['state'] == 'setup':
        return ['place_p0:0,0', 'place_p0:0,1', 'place_p0:1,0', 'place_p0:1,1', 'place_p1:3,3', 'place_p1:3,2', 'place_p1:3,1', 'place_p1:3,0']
    else:
        player_id = 'p0' if state['positions']['p0']['row'] != state['positions']['p1']['row'] or state['positions']['p0']['col'] != state['positions']['p1']['col'] else 'p1'
        actions = []
        if player_id == 'p0':
            actions.extend(['Up', 'Down', 'Left', 'Right', 'Stay'])
        else:
            actions.extend(['Up', 'Down', 'Left', 'Right', 'Stay'])
        return actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_loc = state['positions']['p0']['row'], state['positions']['p0']['col']
    p1_loc = state['positions']['p1']['row'], state['positions']['p1']['col']
    p0_quadrant = get_quadrant(state['positions']['p0'])
    p1_quadrant = get_quadrant(state['positions']['p1'])
    return [
        {'my_loc': f"({p0_loc[0]}, {p0_loc[1]}), Quadrant: {p0_quadrant}", 'opp_quadrant': p1_quadrant},
        {'my_loc': f"({p1_loc[0]}, {p1_loc[1]}), Quadrant: {p1_quadrant}", 'opp_quadrant': p0_quadrant}
    ]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # This should be implemented to generate a valid sequence of actions
    # For simplicity, we'll just return a fixed sequence here
    return ['place_p0:0,0', 'Up', 'Down', 'Left', 'Right', 'Stay']