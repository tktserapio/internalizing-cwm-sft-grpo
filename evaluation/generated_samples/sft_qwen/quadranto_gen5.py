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

# Helper functions
def place_player_in_quadrant(player_id: int) -> tuple[int, int]:
    """Randomly places a player in one of the four quadrants."""
    quadrant = random.choice(['Q1', 'Q2', 'Q3', 'Q4'])
    if quadrant == 'Q1':
        row, col = 0, 0
    elif quadrant == 'Q2':
        row, col = 0, 2
    elif quadrant == 'Q3':
        row, col = 2, 0
    else:  # quadrant == 'Q4'
        row, col = 2, 2
    return row, col

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    p0_row, p0_col = place_player_in_quadrant(0)
    p1_row, p1_col = place_player_in_quadrant(1)
    return {
        'p0_loc': (p0_row, p0_col),
        'p1_loc': (p1_row, p1_col),
        'current_player': 0,
        'turn_count': 0,
        'game_over': False,
        'reward': [0.0, 0.0],
        'legal_actions': ['Stay'],
        'observations': [{'loc': (p0_row, p0_col), 'opp_quadrant': 'Bottom-Right'}, {'loc': (p1_row, p1_col), 'opp_quadrant': 'Top-Left'}]
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    current_player = new_state['current_player']
    opponent_loc = new_state['p1_loc'] if current_player == 0 else new_state['p0_loc']
    
    if action == 'Stay':
        new_state['current_player'] = (current_player + 1) % 2
        new_state['legal_actions'].append('Stay')
    else:
        new_state['legal_actions'].remove(action)
        
    if action in ['Up', 'Down', 'Left', 'Right']:
        new_loc = new_state['p0_loc'] if current_player == 0 else new_state['p1_loc']
        if action == 'Up':
            new_loc = (new_loc[0] - 1, new_loc[1])
        elif action == 'Down':
            new_loc = (new_loc[0] + 1, new_loc[1])
        elif action == 'Left':
            new_loc = (new_loc[0], new_loc[1] - 1)
        elif action == 'Right':
            new_loc = (new_loc[0], new_loc[1] + 1)
        new_state['p0_loc'] = new_loc if current_player == 0 else opponent_loc
        new_state['p1_loc'] = new_loc if current_player == 1 else opponent_loc
    
    if new_state['p0_loc'] == new_state['p1_loc']:
        new_state['game_over'] = True
        new_state['reward'] = [-1.0, 1.0]
    elif new_state['turn_count'] >= 20:
        new_state['game_over'] = True
        new_state['reward'] = [0.0, 0.0]
    
    new_state['turn_count'] += 1
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    return state['reward']

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    return state['legal_actions']

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return state['observations']

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to be implemented based on the specific game dynamics and history.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real implementation, this function would be more complex and handle the stochastic nature of the game.
    return ['Right', 'Up', 'Down', 'Left', 'Stay']