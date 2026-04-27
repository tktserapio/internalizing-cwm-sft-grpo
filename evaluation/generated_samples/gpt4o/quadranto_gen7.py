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

# Constants for the game
BOARD_SIZE = 4
QUADRANTS = {
    0: [(0, 0), (0, 1), (1, 0), (1, 1)],  # Top-Left
    1: [(0, 2), (0, 3), (1, 2), (1, 3)],  # Top-Right
    2: [(2, 0), (2, 1), (3, 0), (3, 1)],  # Bottom-Left
    3: [(2, 2), (2, 3), (3, 2), (3, 3)]   # Bottom-Right
}

# Helper function to determine the quadrant of a given position
def get_quadrant(row: int, col: int) -> int:
    for q, positions in QUADRANTS.items():
        if (row, col) in positions:
            return q
    return -1

# Function to initialize the game state
def get_initial_state() -> State:
    p0_start = random.choice(QUADRANTS[0])
    p1_start = random.choice(QUADRANTS[3])
    return {
        "positions": [(p0_start[0], p0_start[1]), (p1_start[0], p1_start[1])],
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }

# Function to apply an action and return the new game state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    positions = list(state["positions"])
    current_player = state["current_player"]

    # Determine the new position based on the action
    row, col = positions[current_player]
    if action == "Up":
        row = max(0, row - 1)
    elif action == "Down":
        row = min(BOARD_SIZE - 1, row + 1)
    elif action == "Left":
        col = max(0, col - 1)
    elif action == "Right":
        col = min(BOARD_SIZE - 1, col + 1)
    # "Stay" means no change in position

    positions[current_player] = (row, col)
    new_state["positions"] = positions
    new_state["turn_count"] += 1

    # Check for win condition
    if positions[0] == positions[1]:
        new_state["game_over"] = True

    # Switch to the other player
    new_state["current_player"] = 1 - current_player

    # Check for draw condition
    if new_state["turn_count"] >= 20:
        new_state["game_over"] = True

    return new_state

# Function to get the current player
def get_current_player(state: State) -> int:
    if state["game_over"]:
        return -1
    return state["current_player"]

# Function to get the player name
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Function to get the rewards for each player
def get_rewards(state: State) -> List[float]:
    if not state["game_over"]:
        return [0.0, 0.0]
    positions = state["positions"]
    if positions[0] == positions[1]:
        winner = 1 - state["current_player"]
        return [1.0 if winner == 0 else -1.0, 1.0 if winner == 1 else -1.0]
    return [0.0, 0.0]

# Function to get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state["game_over"]:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

# Function to get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    positions = state["positions"]
    p0_obs = {
        "My Loc": positions[0],
        "Opponent Quadrant": get_quadrant(*positions[1])
    }
    p1_obs = {
        "My Loc": positions[1],
        "Opponent Quadrant": get_quadrant(*positions[0])
    }
    return [p0_obs, p1_obs]

# Function to resample history (not fully implemented due to stochastic nature)
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function is complex due to the stochastic nature of the game
    # For simplicity, we assume a simple strategy of repeating the last known action
    return [action for _, action in obs_action_history if action is not None]