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
def place_player(row, col, player_id):
    """Place a player in a given row and column."""
    return {f"place_{player_id}": f"{row},{col}"}

def generate_random_initial_state():
    """Generate a random initial state."""
    # Randomly place player 0 in Q1 and player 1 in Q4
    q1 = [(0, 0), (0, 1), (1, 0), (1, 1)]
    q2 = [(0, 2), (0, 3), (1, 2), (1, 3)]
    q3 = [(2, 0), (2, 1), (3, 0), (3, 1)]
    q4 = [(2, 2), (2, 3), (3, 2), (3, 3)]

    player_0_start = random.choice(q1)
    player_1_start = random.choice(q4)

    return {
        "state": {
            "player_0_loc": player_0_start,
            "player_1_loc": player_1_start,
            "current_player": 0,
            "turn_count": 0,
            "player_0_quadrant": "Q1",
            "player_1_quadrant": "Q4"
        }
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = get_current_player(new_state)
    player_loc = new_state[f"player_{player_id}_loc"]
    opponent_quadrant = new_state[f"player_{1-player_id}_quadrant"]

    if action == "Stay":
        new_state[f"player_{player_id}_loc"] = player_loc
    elif action in ["Up", "Down", "Left", "Right"]:
        new_loc = move(player_loc, action)
        new_state[f"player_{player_id}_loc"] = new_loc
        new_state[f"player_{1-player_id}_quadrant"] = get_opponent_quadrant(new_loc, opponent_quadrant)

    new_state["turn_count"] += 1
    new_state["current_player"] = 1 - new_state["current_player"]

    return new_state

def move(loc, direction):
    """Move a player in a given direction."""
    row, col = loc
    if direction == "Up":
        row -= 1
    elif direction == "Down":
        row += 1
    elif direction == "Left":
        col -= 1
    elif direction == "Right":
        col += 1
    return (row, col)

def get_opponent_quadrant(loc, opponent_quadrant):
    """Determine the quadrant of the opponent based on the player's location."""
    if opponent_quadrant == "Q1":
        return "Q4" if loc in [(0, 0), (0, 1), (1, 0), (1, 1)] else "Q1"
    elif opponent_quadrant == "Q2":
        return "Q1" if loc in [(0, 2), (0, 3), (1, 2), (1, 3)] else "Q2"
    elif opponent_quadrant == "Q3":
        return "Q4" if loc in [(2, 0), (2, 1), (3, 0), (3, 1)] else "Q3"
    elif opponent_quadrant == "Q4":
        return "Q3" if loc in [(2, 2), (2, 3), (3, 2), (3, 3)] else "Q4"

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    player_0_loc = state["player_0_loc"]
    player_1_loc = state["player_1_loc"]
    if player_0_loc == player_1_loc:
        return [-1.0, 1.0]
    elif state["turn_count"] >= 20:
        return [0.0, 0.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_id = get_current_player(state)
    if state["turn_count"] >= 20:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_loc = state["player_0_loc"]
    player_1_loc = state["player_1_loc"]
    player_0_quadrant = state["player_0_quadrant"]
    player_1_quadrant = state["player_1_quadrant"]
    return [
        {"my_loc": player_0_loc, "opponent_loc": player_1_loc, "opponent_quadrant": player_1_quadrant},
        {"my_loc": player_1_loc, "opponent_loc": player_0_loc, "opponent_quadrant": player_0_quadrant}
    ]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    return obs_action_history[-1][1] if obs_action_history else ["Stay"] * 20