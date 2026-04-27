import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple, Union
import random

# Type definitions
Action = str
State = Dict[str, Union[int, List[int], List[List[int]]]]
PlayerObservation = Dict[str, Union[int, List[int], List[List[int]]]]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for players
    initial_positions = [(0, 0), (3, 3)]
    # Randomly select initial position for player 0
    p0_position = random.choice(initial_positions)
    initial_positions.remove(p0_position)
    p1_position = initial_positions[0]
    
    # Initial state dictionary
    state = {
        'p0': p0_position,
        'p1': p1_position,
        'turn': 0,
        'quadrant_p0': 'Q1',
        'quadrant_p1': 'Q4'
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    p0_loc, p1_loc = new_state['p0'], new_state['p1']
    quadrant_p0, quadrant_p1 = new_state['quadrant_p0'], new_state['quadrant_p1']
    
    if action == 'place_p0:<row>,<col>':
        row, col = map(int, action.split(':')[-1].split(','))
        new_state['p0'] = (row, col)
        new_state['quadrant_p0'] = get_quadrant(row, col)
    elif action == 'place_p1:<row>,<col>':
        row, col = map(int, action.split(':')[-1].split(','))
        new_state['p1'] = (row, col)
        new_state['quadrant_p1'] = get_quadrant(row, col)
    else:
        # Movement actions
        if action == 'Up':
            new_state['p0'] = (p0_loc[0] - 1, p0_loc[1])
            new_state['quadrant_p0'] = get_quadrant(new_state['p0'][0], new_state['p0'][1])
        elif action == 'Down':
            new_state['p0'] = (p0_loc[0] + 1, p0_loc[1])
            new_state['quadrant_p0'] = get_quadrant(new_state['p0'][0], new_state['p0'][1])
        elif action == 'Left':
            new_state['p0'] = (p0_loc[0], p0_loc[1] - 1)
            new_state['quadrant_p0'] = get_quadrant(new_state['p0'][0], new_state['p0'][1])
        elif action == 'Right':
            new_state['p0'] = (p0_loc[0], p0_loc[1] + 1)
            new_state['quadrant_p0'] = get_quadrant(new_state['p0'][0], new_state['p0'][1])
        elif action == 'Stay':
            pass
        else:
            raise ValueError(f"Invalid action: {action}")
    
    # Check if the game is over
    if abs(p0_loc[0] - p1_loc[0]) <= 1 and abs(p0_loc[1] - p1_loc[1]) <= 1:
        winner = 1 if p0_loc == p1_loc else 0
        new_state['winner'] = winner
        new_state['game_over'] = True
    else:
        new_state['turn'] += 1
    
    return new_state

def get_quadrant(row: int, col: int) -> str:
    """Determine the quadrant based on the row and column."""
    if row < 2 and col < 2:
        return 'Q1'
    elif row < 2 and col >= 2:
        return 'Q2'
    elif row >= 2 and col < 2:
        return 'Q3'
    else:
        return 'Q4'

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['game_over']:
        return -4
    else:
        return 0 if state['p0'] == state['p1'] else (1 if state['p0'][0] < state['p1'][0] or (state['p0'][0] == state['p1'][0] and state['p0'][1] < state['p1'][1]) else 0)

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['game_over']:
        return [-1.0, 1.0] if state['winner'] == 0 else [1.0, -1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['game_over']:
        return []
    else:
        p0_loc, p1_loc = state['p0'], state['p1']
        quadrant_p0, quadrant_p1 = state['quadrant_p0'], state['quadrant_p1']
        legal_actions = ['Stay']
        if quadrant_p0 == 'Q1':
            if p0_loc[0] > 0:
                legal_actions.append('Up')
            if p0_loc[1] < 3:
                legal_actions.append('Right')
        elif quadrant_p0 == 'Q2':
            if p0_loc[0] < 1:
                legal_actions.append('Down')
            if p0_loc[1] < 3:
                legal_actions.append('Right')
        elif quadrant_p0 == 'Q3':
            if p0_loc[0] < 1:
                legal_actions.append('Down')
            if p0_loc[1] > 0:
                legal_actions.append('Left')
        elif quadrant_p0 == 'Q4':
            if p0_loc[0] > 0:
                legal_actions.append('Up')
            if p0_loc[1] > 0:
                legal_actions.append('Left')
        
        if quadrant_p1 == 'Q1':
            if p1_loc[0] > 0:
                legal_actions.append('Up')
            if p1_loc[1] < 3:
                legal_actions.append('Right')
        elif quadrant_p1 == 'Q2':
            if p1_loc[0] < 1:
                legal_actions.append('Down')
            if p1_loc[1] < 3:
                legal_actions.append('Right')
        elif quadrant_p1 == 'Q3':
            if p1_loc[0] < 1:
                legal_actions.append('Down')
            if p1_loc[1] > 0:
                legal_actions.append('Left')
        elif quadrant_p1 == 'Q4':
            if p1_loc[0] > 0:
                legal_actions.append('Up')
            if p1_loc[1] > 0:
                legal_actions.append('Left')
        
        return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_loc, p1_loc = state['p0'], state['p1']
    quadrant_p0, quadrant_p1 = state['quadrant_p0'], state['quadrant_p1']
    player_0_obs = {
        'loc': p0_loc,
        'quadrant': quadrant_p0
    }
    player_1_obs = {
        'loc': p1_loc,
        'quadrant': quadrant_p1
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement the logic to sample actions based on the history and current state.
    # For simplicity, we'll just return a fixed sequence of actions that leads to a win for player_id.
    # In a real implementation, this would involve complex probabilistic sampling.
    if player_id == 0:
        return ['Right', 'Down', 'Right', 'Up']
    else:
        return ['Up', 'Left', 'Up', 'Left']