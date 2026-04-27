import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to generate a random position within a quadrant
def random_position_in_quadrant(quadrant: str) -> Tuple[int, int]:
    rows, cols = (2, 2) if quadrant == 'Q1' else (1, 2) if quadrant == 'Q2' else (2, 1) if quadrant == 'Q3' else (1, 1)
    row = random.randint(0, rows - 1)
    col = random.randint(0, cols - 1)
    return row, col

# Required Functions
def get_initial_state() -> State:
    # Initial state setup
    state = {
        'player_0_loc': random_position_in_quadrant('Q1'),
        'player_1_loc': random_position_in_quadrant('Q4'),
        'turn_count': 0,
        'current_player': 0,
        'game_over': False,
        'player_0_quadrant': 'Q1',
        'player_1_quadrant': 'Q4'
    }
    return state

def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    
    if action == 'place_p0:<row>,<col>':
        new_state['player_0_loc'] = eval(action.split(':')[-1])
        new_state['player_0_quadrant'] = get_quadrant(new_state['player_0_loc'])
    elif action == 'place_p1:<row>,<col>':
        new_state['player_1_loc'] = eval(action.split(':')[-1])
        new_state['player_1_quadrant'] = get_quadrant(new_state['player_1_loc'])
    else:
        new_state['turn_count'] += 1
        new_state['current_player'] = 1 if new_state['current_player'] == 0 else 0
        
        if action == 'Up':
            new_state['player_0_loc'] = (new_state['player_0_loc'][0], max(0, new_state['player_0_loc'][1] - 1))
            new_state['player_1_loc'] = (new_state['player_1_loc'][0], min(3, new_state['player_1_loc'][1] + 1))
        elif action == 'Down':
            new_state['player_0_loc'] = (new_state['player_0_loc'][0], min(3, new_state['player_0_loc'][1] + 1))
            new_state['player_1_loc'] = (new_state['player_1_loc'][0], max(0, new_state['player_1_loc'][1] - 1))
        elif action == 'Left':
            new_state['player_0_loc'] = (max(0, new_state['player_0_loc'][0] - 1), new_state['player_0_loc'][1])
            new_state['player_1_loc'] = (min(3, new_state['player_1_loc'][0] + 1), new_state['player_1_loc'][1])
        elif action == 'Right':
            new_state['player_0_loc'] = (min(3, new_state['player_0_loc'][0] + 1), new_state['player_0_loc'][1])
            new_state['player_1_loc'] = (max(0, new_state['player_1_loc'][0] - 1), new_state['player_1_loc'][1])
        elif action == 'Stay':
            pass
        
        if new_state['player_0_loc'] == new_state['player_1_loc']:
            new_state['game_over'] = True
            new_state['winner'] = 1 if new_state['current_player'] == 1 else 0
            new_state['loser'] = 0 if new_state['current_player'] == 1 else 1
            new_state['reward'] = [new_state['winner'], new_state['loser']]
        else:
            new_state['reward'] = [0.0, 0.0]
    
    return new_state

def get_quadrant(loc: Tuple[int, int]) -> str:
    row, col = loc
    if row < 2 and col < 2:
        return 'Q1'
    elif row < 2 and col >= 2:
        return 'Q2'
    elif row >= 2 and col < 2:
        return 'Q3'
    else:
        return 'Q4'

def get_current_player(state: State) -> int:
    return state['current_player']

def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    return state['reward']

def get_legal_actions(state: State) -> List[Action]:
    current_player = state['current_player']
    legal_actions = []
    
    if not state['game_over']:
        if current_player == 0:
            legal_actions.extend(['Up', 'Down', 'Left', 'Right', 'Stay'])
        else:
            legal_actions.extend(['Up', 'Down', 'Left', 'Right', 'Stay'])
    else:
        legal_actions.append('place_p0:<row>,<col>')
        legal_actions.append('place_p1:<row>,<col>')
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    player_0_loc = state['player_0_loc']
    player_1_loc = state['player_1_loc']
    player_0_quadrant = state['player_0_quadrant']
    player_1_quadrant = state['player_1_quadrant']
    
    player_0_obs = {
        'Loc': player_0_loc,
        'OpponentLoc': player_1_loc,
        'OpponentQuadrant': player_1_quadrant
    }
    player_1_obs = {
        'Loc': player_1_loc,
        'OpponentLoc': player_0_loc,
        'OpponentQuadrant': player_0_quadrant
    }
    
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would need to be implemented based on the specific rules of the game and the observations made.
    # For simplicity, we will just return a fixed sequence of actions.
    # In a real scenario, this function would be more complex and stochastic.
    if player_id == 0:
        return ['Right', 'Up', 'Down', 'Left', 'Stay']
    else:
        return ['Up', 'Down', 'Left', 'Right', 'Stay']