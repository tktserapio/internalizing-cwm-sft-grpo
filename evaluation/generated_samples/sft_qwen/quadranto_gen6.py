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
def place_player_in_quadrant(player_id: int, quadrant: str) -> tuple[int, int]:
    """Randomly places a player in a quadrant and returns its coordinates."""
    quadrants = {
        'Q1': [(0, 0), (0, 1), (1, 0), (1, 1)],
        'Q2': [(0, 2), (0, 3), (1, 2), (1, 3)],
        'Q3': [(2, 0), (2, 1), (3, 0), (3, 1)],
        'Q4': [(2, 2), (2, 3), (3, 2), (3, 3)]
    }
    quadrant_coords = quadrants[quadrant]
    return random.choice(quadrant_coords)

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Place players in different quadrants
    p0_loc = place_player_in_quadrant(0, 'Q1')
    p1_loc = place_player_in_quadrant(1, 'Q4')
    return {
        'p0_loc': p0_loc,
        'p1_loc': p1_loc,
        'turn_count': 0,
        'legal_actions': ['Stay', 'Up', 'Down', 'Left', 'Right'],
        'current_player': 0,
        'game_over': False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action == 'Stay':
        new_state['p0_loc'] = state['p0_loc']
        new_state['p1_loc'] = state['p1_loc']
    else:
        if action in ('Up', 'Down'):
            row = state['p0_loc'][0] + (-1 if action == 'Up' else 1)
            new_state['p0_loc'] = (row, state['p0_loc'][1])
        elif action in ('Left', 'Right'):
            col = state['p0_loc'][1] + (-1 if action == 'Left' else 1)
            new_state['p0_loc'] = (state['p0_loc'][0], col)
        new_state['turn_count'] += 1
        if new_state['p0_loc'] == new_state['p1_loc']:
            new_state['game_over'] = True
            new_state['winner'] = 0
            new_state['loser'] = 1
            new_state['rewards'] = [1.0, -1.0]
        elif new_state['turn_count'] >= 20:
            new_state['game_over'] = True
            new_state['winner'] = 0
            new_state['loser'] = 1
            new_state['rewards'] = [0.0, 0.0]
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    return state['rewards']

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['game_over']:
        return []
    return state['legal_actions']

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_obs = {
        'my_loc': state['p0_loc'],
        'opponent_quadrant': 'Q1' if state['p1_loc'] in [('2', '0'), ('2', '1'), ('3', '0'), ('3', '1')] else 'Q4'
    }
    p1_obs = {
        'my_loc': state['p1_loc'],
        'opponent_quadrant': 'Q1' if state['p0_loc'] in [('2', '0'), ('2', '1'), ('3', '0'), ('3', '1')] else 'Q4'
    }
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to be implemented based on the specific requirements of the game.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real scenario, this function would generate a sequence of actions that could lead to the given observations.
    # Here, we're returning a fixed sequence of actions as a placeholder.
    return ['Right', 'Up', 'Down', 'Left', 'Right', 'Up']