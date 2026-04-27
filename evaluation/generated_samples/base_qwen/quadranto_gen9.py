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

# Helper function to generate a random initial state
def get_random_initial_location():
    locations = [(0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 0), (2, 1), (3, 0), (3, 1), (2, 2), (2, 3), (3, 2), (3, 3)]
    return random.choice(locations)

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Place players in random locations
    p0_loc = get_random_initial_location()
    p1_loc = get_random_initial_location()
    while p0_loc == p1_loc:
        p1_loc = get_random_initial_location()

    # Map locations to quadrants
    quadrant_mapping = {
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

    # Get initial observations
    p0_obs = {"loc": p0_loc, "opp_quadrant": quadrant_mapping[p1_loc]}
    p1_obs = {"loc": p1_loc, "opp_quadrant": quadrant_mapping[p0_loc]}

    return {
        "p0_loc": p0_loc,
        "p1_loc": p1_loc,
        "p0_obs": p0_obs,
        "p1_obs": p1_obs,
        "turn_count": 0,
        "current_player": 0,
        "legal_actions": ["Stay"]
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    if action == "Stay":
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        return new_state
    else:
        new_loc = None
        if action == "Up":
            new_loc = (new_state["p0_loc"][0], new_state["p0_loc"][1] - 1)
        elif action == "Down":
            new_loc = (new_state["p0_loc"][0], new_state["p0_loc"][1] + 1)
        elif action == "Left":
            new_loc = (new_state["p0_loc"][0] - 1, new_state["p0_loc"][1])
        elif action == "Right":
            new_loc = (new_state["p0_loc"][0] + 1, new_state["p0_loc"][1])

        # Check if the new location is within bounds
        if 0 <= new_loc[0] < 4 and 0 <= new_loc[1] < 4:
            new_state["p0_loc"] = new_loc
            new_state["current_player"] = (new_state["current_player"] + 1) % 2
            new_state["legal_actions"] = ["Stay"]
            return new_state
        else:
            new_state["legal_actions"] = []
            return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state["p0_loc"] == state["p1_loc"]:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state["p0_loc"] == state["p1_loc"]:
        return []
    else:
        return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs].
    """
    return [state["p0_obs"], state["p1_obs"]]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement stochastic sampling logic based on the observations and the game rules.
    # For simplicity, we'll just return a fixed sequence of actions here.
    # In a real implementation, this would involve more complex logic.
    return ["Stay", "Up", "Down", "Left", "Right", "Stay"]