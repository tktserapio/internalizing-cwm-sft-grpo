import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple, Union

Action = str
State = Dict[str, Union[int, List[int], List[List[int]]]]
PlayerObservation = Dict[str, Union[int, List[int], List[List[int]]]]

def get_initial_state() -> State:
    # Initial state setup
    initial_board = [[0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
    initial_quadrant_mapping = {
        0: [(0, 0), (0, 1), (1, 0), (1, 1)],
        1: [(0, 2), (0, 3), (1, 2), (1, 3)],
        2: [(2, 0), (2, 1), (3, 0), (3, 1)],
        3: [(2, 2), (2, 3), (3, 2), (3, 3)]
    }
    
    # Randomly place player 0 in Q1
    player_0_row, player_0_col = initial_quadrant_mapping[0][int(len(initial_quadrant_mapping[0]) / 2)]
    initial_board[player_0_row][player_0_col] = 0
    
    # Randomly place player 1 in Q4
    player_1_row, player_1_col = initial_quadrant_mapping[3][int(len(initial_quadrant_mapping[3]) / 2)]
    initial_board[player_1_row][player_1_col] = 1
    
    return {
        'board': initial_board,
        'player_0_loc': [player_0_row, player_0_col],
        'player_1_loc': [player_1_row, player_1_col],
        'turn_count': 0,
        'player_0_quadrant': 0,
        'player_1_quadrant': 3
    }

def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    player_id = get_current_player(new_state)
    opponent_id = 1 if player_id == 0 else 0
    
    # Update player location based on action
    if action == 'Stay':
        pass
    elif action == 'Left':
        new_state['player_0_loc'][1] -= 1 if new_state['player_0_loc'][1] > 0 else 0
    elif action == 'Right':
        new_state['player_0_loc'][1] += 1 if new_state['player_0_loc'][1] < 3 else 0
    elif action == 'Up':
        new_state['player_0_loc'][0] -= 1 if new_state['player_0_loc'][0] > 0 else 0
    elif action == 'Down':
        new_state['player_0_loc'][0] += 1 if new_state['player_0_loc'][0] < 3 else 0
    
    # Update opponent location based on action
    if action == 'Stay':
        pass
    elif action == 'Left':
        new_state['player_1_loc'][1] -= 1 if new_state['player_1_loc'][1] > 0 else 0
    elif action == 'Right':
        new_state['player_1_loc'][1] += 1 if new_state['player_1_loc'][1] < 3 else 0
    elif action == 'Up':
        new_state['player_1_loc'][0] -= 1 if new_state['player_1_loc'][0] > 0 else 0
    elif action == 'Down':
        new_state['player_1_loc'][0] += 1 if new_state['player_1_loc'][0] < 3 else 0
    
    # Determine if the game is over
    if new_state['player_0_loc'] == new_state['player_1_loc']:
        new_state['game_over'] = True
        new_state['winner'] = player_id
        new_state['loser'] = opponent_id
    else:
        new_state['game_over'] = False
        new_state['winner'] = None
        new_state['loser'] = None
    
    return new_state

def get_current_player(state: State) -> int:
    return state['winner'] if state['game_over'] else -4

def get_player_name(player_id: int) -> str:
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> List[float]:
    if state['game_over']:
        return [state['winner'], -state['winner']]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    player_id = get_current_player(state)
    if state['game_over']:
        return []
    elif player_id == 0:
        return ['Up', 'Down', 'Left', 'Right', 'Stay']
    else:
        return ['Up', 'Down', 'Left', 'Right', 'Stay']

def get_observations(state: State) -> List[PlayerObservation]:
    player_0_loc = state['player_0_loc']
    player_1_loc = state['player_1_loc']
    player_0_quadrant = state['player_0_quadrant']
    player_1_quadrant = state['player_1_quadrant']
    
    player_0_obs = {
        'Loc': player_0_loc,
        'OpponentQuadrant': player_1_quadrant
    }
    
    player_1_obs = {
        'Loc': player_1_loc,
        'OpponentQuadrant': player_0_quadrant
    }
    
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would need to implement stochastic sampling logic here
    # For simplicity, we'll just return a fixed sequence of actions
    # In a real implementation, this should be more complex and stochastic
    if player_id == 0:
        return ['Right', 'Up', 'Down', 'Left', 'Stay']
    else:
        return ['Up', 'Down', 'Left', 'Right', 'Stay']