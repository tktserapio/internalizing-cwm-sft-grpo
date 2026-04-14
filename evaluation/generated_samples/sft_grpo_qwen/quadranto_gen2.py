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
    # Observations for both players
    observations = [
        {'my_loc': f"({initial_positions['p0']['row']},{initial_positions['p0']['col']}), Quadrant: Top-Left", 'opp_quadrant': 'Bottom-Right'},
        {'my_loc': f"({initial_positions['p1']['row']},{initial_positions['p1']['col']}), Quadrant: Bottom-Right", 'opp_quadrant': 'Top-Left'}
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
    player_id = get_current_player(new_state)
    player = new_state['positions'][f'p{player_id}']
    
    if action == 'place_p0:<row>,<col>':
        row, col = map(int, action.split(':')[-1].split(','))
        new_state['positions']['p0'] = {'row': row, 'col': col}
        new_state['observations'][0]['my_loc'] = f"({row},{col}), Quadrant: Top-Left"
        new_state['observations'][0]['opp_quadrant'] = 'Bottom-Right'
        new_state['state'] = 'movement'
        return new_state
    
    if action == 'place_p1:<row>,<col>':
        row, col = map(int, action.split(':')[-1].split(','))
        new_state['positions']['p1'] = {'row': row, 'col': col}
        new_state['observations'][1]['my_loc'] = f"({row},{col}), Quadrant: Bottom-Right"
        new_state['observations'][1]['opp_quadrant'] = 'Top-Left'
        new_state['state'] = 'movement'
        return new_state
    
    if action in ['Up', 'Down', 'Left', 'Right', 'Stay']:
        player['row'], player['col'] = update_position(player, action)
        new_state['positions'][f'p{player_id}'] = player
        new_state['observations'][0]['my_loc'] = f"({player['row']},{player['col']}), Quadrant: Top-Left"
        new_state['observations'][1]['my_loc'] = f"({player['row']},{player['col']}), Quadrant: Bottom-Right"
        new_state['state'] = 'movement'
        return new_state
    
    raise ValueError("Invalid action")

def update_position(player: dict, action: str) -> tuple[int, int]:
    """Updates the position of the player based on the given action."""
    row, col = player['row'], player['col']
    if action == 'Up':
        row -= 1
    elif action == 'Down':
        row += 1
    elif action == 'Left':
        col -= 1
    elif action == 'Right':
        col += 1
    elif action == 'Stay':
        pass
    return row, col

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['state'] == 'setup':
        return -4
    else:
        return 0 if state['positions']['p0']['row'] < state['positions']['p1']['row'] else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f'p{player_id}'

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['state'] == 'setup':
        return [0.0, 0.0]
    else:
        p0_row, p1_row = state['positions']['p0']['row'], state['positions']['p1']['row']
        if p0_row == p1_row and p0_row > -1:
            return [-1.0, 1.0]
        else:
            return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['state'] == 'setup':
        return []
    else:
        player_id = get_current_player(state)
        player = state['positions'][f'p{player_id}']
        legal_moves = ['Up', 'Down', 'Left', 'Right', 'Stay']
        if player['row'] == 0:
            legal_moves.remove('Up')
        if player['row'] == 3:
            legal_moves.remove('Down')
        if player['col'] == 0:
            legal_moves.remove('Left')
        if player['col'] == 3:
            legal_moves.remove('Right')
        return legal_moves

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = state['observations'][0]
    player_1_obs = state['observations'][1]
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # This should be implemented to generate a plausible sequence of actions
    # that could have led to the current observations.
    # For simplicity, we'll just return a random sequence of actions.
    legal_actions = get_legal_actions(get_initial_state())
    return [random.choice(legal_actions) for _ in range(len(obs_action_history))]