import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def place_player(state: State, player_id: int, row: int, col: int) -> State:
    """Place a player in the given position in the state."""
    state[f"player_{player_id}_loc"] = (row, col)
    return state

def update_quadrant(state: State, player_id: int, row: int, col: int) -> State:
    """Update the quadrant of the player based on their location."""
    quadrant = {
        (0, 0): "Q1",
        (0, 1): "Q1",
        (1, 0): "Q1",
        (1, 1): "Q1",
        (0, 2): "Q2",
        (0, 3): "Q2",
        (1, 2): "Q2",
        (1, 3): "Q2",
        (2, 0): "Q3",
        (2, 1): "Q3",
        (3, 0): "Q3",
        (3, 1): "Q3",
        (2, 2): "Q4",
        (2, 3): "Q4",
        (3, 2): "Q4",
        (3, 3): "Q4"
    }
    state[f"player_{player_id}_quadrant"] = quadrant[(row, col)]
    return state

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    state = {}
    # Place player 0 in Q1 randomly
    state = place_player(state, 0, random.choice([0, 0]), random.choice([0, 1]))
    # Place player 1 in Q4 randomly
    state = place_player(state, 1, random.choice([3, 3]), random.choice([2, 3]))
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    player_id = get_current_player(new_state)
    if action == "Stay":
        new_state[f"player_{player_id}_loc"] = new_state[f"player_{player_id}_loc"]
    elif action in ["Up", "Down", "Left", "Right"]:
        row, col = new_state[f"player_{player_id}_loc"]
        if action == "Up":
            new_state[f"player_{player_id}_loc"] = (row - 1, col)
        elif action == "Down":
            new_state[f"player_{player_id}_loc"] = (row + 1, col)
        elif action == "Left":
            new_state[f"player_{player_id}_loc"] = (row, col - 1)
        elif action == "Right":
            new_state[f"player_{player_id}_loc"] = (row, col + 1)
    new_state = update_quadrant(new_state, player_id, *new_state[f"player_{player_id}_loc"])
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    player_0_loc = state.get(f"player_0_loc")
    player_1_loc = state.get(f"player_1_loc")
    if player_0_loc and player_1_loc:
        return 0 if player_0_loc == player_1_loc else 1
    return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    player_0_loc = state.get(f"player_0_loc")
    player_1_loc = state.get(f"player_1_loc")
    if player_0_loc and player_1_loc and player_0_loc == player_1_loc:
        return [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_0_loc = state.get(f"player_0_loc")
    player_1_loc = state.get(f"player_1_loc")
    if player_0_loc and player_1_loc and player_0_loc == player_1_loc:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_loc = state.get(f"player_0_loc")
    player_1_loc = state.get(f"player_1_loc")
    player_0_quadrant = state.get(f"player_0_quadrant")
    player_1_quadrant = state.get(f"player_1_quadrant")
    player_0_obs = {
        "My Loc": f"({player_0_loc[0]}, {player_0_loc[1]})",
        "Opponent Quadrant": player_1_quadrant
    }
    player_1_obs = {
        "My Loc": f"({player_1_loc[0]}, {player_1_loc[1]})",
        "Opponent Quadrant": player_0_quadrant
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    # This should be replaced with actual resampling logic
    return ["Right", "Up", "Down", "Left", "Stay"]