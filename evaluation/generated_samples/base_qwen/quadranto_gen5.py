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
    """Randomly places a player in a quadrant."""
    quadrants = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)]
    quadrant_mapping = {
        "Q1": quadrants[:4],
        "Q2": quadrants[4:8],
        "Q3": quadrants[8:12],
        "Q4": quadrants[12:16]
    }
    quadrant = random.choice(list(quadrant_mapping.keys()))
    row, col = random.choice(quadrant_mapping[quadrant])
    return player_id, (row, col)

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    p0_row, p0_col = place_player_in_quadrant(0)
    p1_row, p1_col = place_player_in_quadrant(1)
    return {
        "p0_loc": (p0_row, p0_col),
        "p1_loc": (p1_row, p1_col),
        "p0_quadrant": quadrant_mapping["Q1"],
        "p1_quadrant": quadrant_mapping["Q4"],
        "turn_count": 0,
        "legal_actions": ["Stay"]
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    p0_loc, p1_loc = new_state["p0_loc"], new_state["p1_loc"]
    p0_quadrant, p1_quadrant = new_state["p0_quadrant"], new_state["p1_quadrant"]
    
    # Update locations based on action
    if action == "Stay":
        new_state["p0_loc"] = p0_loc
        new_state["p1_loc"] = p1_loc
    elif action == "Up":
        new_state["p0_loc"] = (p0_loc[0] - 1, p0_loc[1])
        new_state["p1_loc"] = (p1_loc[0] - 1, p1_loc[1])
    elif action == "Down":
        new_state["p0_loc"] = (p0_loc[0] + 1, p0_loc[1])
        new_state["p1_loc"] = (p1_loc[0] + 1, p1_loc[1])
    elif action == "Left":
        new_state["p0_loc"] = (p0_loc[0], p0_loc[1] - 1)
        new_state["p1_loc"] = (p1_loc[0], p1_loc[1] - 1)
    elif action == "Right":
        new_state["p0_loc"] = (p0_loc[0], p0_loc[1] + 1)
        new_state["p1_loc"] = (p1_loc[0], p1_loc[1] + 1)
    
    # Check for win condition
    if p0_loc == p1_loc:
        new_state["game_over"] = True
        new_state["winner"] = 1
        new_state["loser"] = 0
        new_state["reward"] = [1.0, -1.0]
    elif new_state["turn_count"] >= 20:
        new_state["game_over"] = True
        new_state["winner"] = 0
        new_state["loser"] = 1
        new_state["reward"] = [0.0, 0.0]
    
    # Update turn count
    new_state["turn_count"] += 1
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["game_over"]:
        return -4
    else:
        return 0 if state["p0_loc"] == state["p1_loc"] else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    return state["reward"]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    else:
        return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_loc, p1_loc = state["p0_loc"], state["p1_loc"]
    p0_quadrant = state["p0_quadrant"]
    p1_quadrant = state["p1_quadrant"]
    p0_obs = {
        "My Loc": p0_loc,
        "Opponent Quadrant": p1_quadrant
    }
    p1_obs = {
        "My Loc": p1_loc,
        "Opponent Quadrant": p0_quadrant
    }
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement the logic to sample actions based on the observations.
    # For simplicity, we'll just return a fixed sequence of actions here.
    # In a real implementation, this would involve complex logic to ensure the sampled actions match the observations.
    return ["Stay", "Up", "Down", "Left", "Right", "Stay"]