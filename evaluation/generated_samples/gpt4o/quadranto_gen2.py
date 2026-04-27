import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
GRID_SIZE = 4
MAX_TURNS = 20
PLAYER_0 = 0
PLAYER_1 = 1
TERMINAL_STATE = -4

# Quadrants
QUADRANTS = {
    (0, 0): "Top-Left",
    (0, 1): "Top-Left",
    (1, 0): "Top-Left",
    (1, 1): "Top-Left",
    (0, 2): "Top-Right",
    (0, 3): "Top-Right",
    (1, 2): "Top-Right",
    (1, 3): "Top-Right",
    (2, 0): "Bottom-Left",
    (2, 1): "Bottom-Left",
    (3, 0): "Bottom-Left",
    (3, 1): "Bottom-Left",
    (2, 2): "Bottom-Right",
    (2, 3): "Bottom-Right",
    (3, 2): "Bottom-Right",
    (3, 3): "Bottom-Right"
}

# Helper function to determine the quadrant of a position
def get_quadrant(position: Tuple[int, int]) -> str:
    return QUADRANTS[position]

# Function to get the initial state
def get_initial_state() -> State:
    # Randomly place players in their respective starting quadrants
    p0_position = random.choice([(0, 0), (0, 1), (1, 0), (1, 1)])
    p1_position = random.choice([(2, 2), (2, 3), (3, 2), (3, 3)])
    return {
        'positions': {PLAYER_0: p0_position, PLAYER_1: p1_position},
        'turn_count': 0,
        'current_player': PLAYER_0,
        'game_over': False
    }

# Function to apply an action and return a new state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    new_state['positions'] = state['positions'].copy()
    
    if state['game_over']:
        return new_state

    current_player = state['current_player']
    position = state['positions'][current_player]
    new_position = move(position, action)

    # Update the player's position
    new_state['positions'][current_player] = new_position

    # Check if the current player has caught the other player
    if new_position == new_state['positions'][1 - current_player]:
        new_state['game_over'] = True
    else:
        # Update turn count and switch player
        new_state['turn_count'] += 1
        if new_state['turn_count'] >= MAX_TURNS:
            new_state['game_over'] = True
        else:
            new_state['current_player'] = 1 - current_player

    return new_state

# Helper function to move a player
def move(position: Tuple[int, int], action: Action) -> Tuple[int, int]:
    x, y = position
    if action == "Up" and x > 0:
        x -= 1
    elif action == "Down" and x < GRID_SIZE - 1:
        x += 1
    elif action == "Left" and y > 0:
        y -= 1
    elif action == "Right" and y < GRID_SIZE - 1:
        y += 1
    # "Stay" or invalid moves result in no change
    return (x, y)

# Function to get the current player
def get_current_player(state: State) -> int:
    if state['game_over']:
        return TERMINAL_STATE
    return state['current_player']

# Function to get the player name
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Function to get the rewards
def get_rewards(state: State) -> List[float]:
    if not state['game_over']:
        return [0.0, 0.0]
    
    p0_pos = state['positions'][PLAYER_0]
    p1_pos = state['positions'][PLAYER_1]
    
    if p0_pos == p1_pos:
        if state['current_player'] == PLAYER_0:
            return [1.0, -1.0]
        else:
            return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

# Function to get legal actions
def get_legal_actions(state: State) -> List[Action]:
    if state['game_over']:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

# Function to get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    p0_pos = state['positions'][PLAYER_0]
    p1_pos = state['positions'][PLAYER_1]
    return [
        {
            "My Loc": p0_pos,
            "Opponent Quadrant": get_quadrant(p1_pos)
        },
        {
            "My Loc": p1_pos,
            "Opponent Quadrant": get_quadrant(p0_pos)
        }
    ]

# Function to resample history
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would typically involve complex logic to reconstruct a sequence of actions
    # that could have led to the given observations. For simplicity, we return an empty list.
    return []