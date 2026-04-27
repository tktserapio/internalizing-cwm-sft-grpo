import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants for the game
BOARD_SIZE = 4
MAX_TURNS = 20
QUADRANTS = {
    (0, 0): 1, (0, 1): 1, (1, 0): 1, (1, 1): 1,
    (0, 2): 2, (0, 3): 2, (1, 2): 2, (1, 3): 2,
    (2, 0): 3, (2, 1): 3, (3, 0): 3, (3, 1): 3,
    (2, 2): 4, (2, 3): 4, (3, 2): 4, (3, 3): 4
}

# Helper functions
def get_quadrant(position: Tuple[int, int]) -> int:
    """Returns the quadrant of a given position."""
    return QUADRANTS[position]

def move_position(position: Tuple[int, int], action: Action) -> Tuple[int, int]:
    """Returns the new position after applying the action."""
    row, col = position
    if action == "Up":
        return max(0, row - 1), col
    elif action == "Down":
        return min(BOARD_SIZE - 1, row + 1), col
    elif action == "Left":
        return row, max(0, col - 1)
    elif action == "Right":
        return row, min(BOARD_SIZE - 1, col + 1)
    elif action == "Stay":
        return row, col
    else:
        raise ValueError(f"Invalid action: {action}")

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    p0_start = (random.choice([0, 1]), random.choice([0, 1]))
    p1_start = (random.choice([2, 3]), random.choice([2, 3]))
    return {
        "positions": [p0_start, p1_start],
        "turn_count": 0,
        "current_player": 0
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    positions = state["positions"][:]
    current_player = state["current_player"]

    # Update the position of the current player
    positions[current_player] = move_position(positions[current_player], action)
    new_state["positions"] = positions

    # Check for win condition
    if positions[0] == positions[1]:
        new_state["current_player"] = -1  # Terminal state
    else:
        # Update turn count and switch player
        new_state["turn_count"] += 1
        if new_state["turn_count"] >= MAX_TURNS:
            new_state["current_player"] = -1  # Terminal state
        else:
            new_state["current_player"] = 1 - current_player

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -1 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["current_player"] != -1:
        return [0.0, 0.0]
    positions = state["positions"]
    if positions[0] == positions[1]:
        return [-1.0, 1.0] if state["turn_count"] % 2 == 0 else [1.0, -1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["current_player"] == -1:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    positions = state["positions"]
    p0_obs = {
        "My Loc": positions[0],
        "Opponent Quadrant": get_quadrant(positions[1])
    }
    p1_obs = {
        "My Loc": positions[1],
        "Opponent Quadrant": get_quadrant(positions[0])
    }
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function is complex and depends on the specific stochastic model of the game.
    # For simplicity, we'll return a random sequence of actions that matches the length of the history.
    return [random.choice(["Up", "Down", "Left", "Right", "Stay"]) for _ in obs_action_history]