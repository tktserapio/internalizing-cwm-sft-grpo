import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to generate a random position within a quadrant
def random_position_in_quadrant(quadrant: str) -> tuple[int, int]:
    row, col = quadrant.split(',')
    row = int(row)
    col = int(col)
    x = random.randint(0, 3)
    y = random.randint(0, 3)
    while (x, y) not in [(row, col), (row + 1, col), (row, col + 1), (row + 1, col + 1)]:
        x = random.randint(0, 3)
        y = random.randint(0, 3)
    return x, y

# Required Functions
def get_initial_state() -> State:
    # Initial positions
    p0_start_quadrant = random.choice(['Q1', 'Q3'])
    p1_start_quadrant = random.choice(['Q2', 'Q4'])
    
    # Randomizing initial positions within the chosen quadrants
    p0_loc = random_position_in_quadrant(p0_start_quadrant)
    p1_loc = random_position_in_quadrant(p1_start_quadrant)
    
    return {
        'p0_loc': p0_loc,
        'p1_loc': p1_loc,
        'turn_count': 0,
        'current_player': random.choice([0, 1]),
        'quadrant_mapping': {
            'Q1': ((0, 0), (0, 1), (1, 0), (1, 1)),
            'Q2': ((0, 2), (0, 3), (1, 2), (1, 3)),
            'Q3': ((2, 0), (2, 1), (3, 0), (3, 1)),
            'Q4': ((2, 2), (2, 3), (3, 2), (3, 3))
        }
    }

def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    current_player = new_state['current_player']
    opponent_quadrant = new_state['quadrant_mapping'][new_state[f'p{1-current_player}_loc'][0]]
    
    if action == 'Stay':
        new_state[f'p{current_player}_loc'] = state[f'p{current_player}_loc']
    elif action in ['Up', 'Down', 'Left', 'Right']:
        new_x, new_y = state[f'p{current_player}_loc']
        if action == 'Up':
            new_x -= 1
        elif action == 'Down':
            new_x += 1
        elif action == 'Left':
            new_y -= 1
        elif action == 'Right':
            new_y += 1
        
        if (new_x, new_y) in new_state[f'p{1-current_player}_loc']:
            new_state[f'p{current_player}_loc'] = new_state[f'p{current_player}_loc'], state[f'p{1-current_player}_loc'][0], state[f'p{1-current_player}_loc'][1]
            new_state['turn_count'] += 1
            new_state['current_player'] = 1 - current_player
        else:
            new_state[f'p{current_player}_loc'] = (new_x, new_y)
    
    return new_state

def get_current_player(state: State) -> int:
    return state['current_player']

def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    if state['turn_count'] >= 20:
        return [0.0, 0.0]
    elif state[f'p{state['current_player']}_loc'] == state[f'p{1-state['current_player']}_loc']:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    current_player = state['current_player']
    if state['turn_count'] >= 20:
        return []
    elif state[f'p{current_player}_loc'] == state[f'p{1-current_player}_loc']:
        return ['Stay']
    else:
        return ['Up', 'Down', 'Left', 'Right']

def get_observations(state: State) -> list[PlayerObservation]:
    p0_loc = state['p0_loc']
    p1_loc = state['p1_loc']
    p0_quadrant = state['quadrant_mapping'][p0_loc[0]]
    p1_quadrant = state['quadrant_mapping'][p1_loc[0]]
    
    p0_obs = {
        'My Loc': p0_loc,
        'Opponent Quadrant': p1_quadrant
    }
    p1_obs = {
        'My Loc': p1_loc,
        'Opponent Quadrant': p0_quadrant
    }
    
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would need to be implemented based on the specific requirements of the game.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real scenario, this function would be stochastic and return a sequence that explains the current observations.
    # Here, we're returning a fixed sequence of actions for demonstration purposes.
    if player_id == 0:
        return ['Right', 'Down', 'Right', 'Up', 'Right', 'Up']
    else:
        return ['Up', 'Left', 'Up', 'Left', 'Up', 'Up']