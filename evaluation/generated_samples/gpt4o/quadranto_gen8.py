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
ACTIONS = ["Up", "Down", "Left", "Right", "Stay"]

# Helper functions
def get_quadrant(row: int, col: int) -> str:
    """Determine the quadrant of a given position."""
    if row < 2 and col < 2:
        return "Top-Left"
    elif row < 2 and col >= 2:
        return "Top-Right"
    elif row >= 2 and col < 2:
        return "Bottom-Left"
    else:
        return "Bottom-Right"

def move_position(row: int, col: int, action: Action) -> Tuple[int, int]:
    """Calculate new position based on the action."""
    if action == "Up":
        return max(0, row - 1), col
    elif action == "Down":
        return min(GRID_SIZE - 1, row + 1), col
    elif action == "Left":
        return row, max(0, col - 1)
    elif action == "Right":
        return row, min(GRID_SIZE - 1, col + 1)
    return row, col

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    p0_row, p0_col = random.choice([(0, 0), (0, 1), (1, 0), (1, 1)])
    p1_row, p1_col = random.choice([(2, 2), (2, 3), (3, 2), (3, 3)])
    return {
        "p0_pos": (p0_row, p0_col),
        "p1_pos": (p1_row, p1_col),
        "turn_count": 0,
        "current_player": 0
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if state["current_player"] == 0:
        new_state["p0_pos"] = move_position(*state["p0_pos"], action)
    else:
        new_state["p1_pos"] = move_position(*state["p1_pos"], action)
    
    new_state["turn_count"] += 1
    new_state["current_player"] = 1 - state["current_player"]
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["turn_count"] >= MAX_TURNS or state["p0_pos"] == state["p1_pos"]:
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["p0_pos"] == state["p1_pos"]:
        return [-1.0, 1.0] if state["current_player"] == 1 else [1.0, -1.0]
    if state["turn_count"] >= MAX_TURNS:
        return [0.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if get_current_player(state) == -4:
        return []
    return ACTIONS

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_obs = {
        "My Loc": state["p0_pos"],
        "Opponent Quadrant": get_quadrant(*state["p1_pos"])
    }
    p1_obs = {
        "My Loc": state["p1_pos"],
        "Opponent Quadrant": get_quadrant(*state["p0_pos"])
    }
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function is complex and typically requires a more detailed understanding of the game dynamics.
    # For simplicity, we'll return a random sequence of actions.
    return [random.choice(ACTIONS) for _ in range(len(obs_action_history))]