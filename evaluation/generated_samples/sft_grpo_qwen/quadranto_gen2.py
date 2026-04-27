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

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions
    p0_position = (random.choice([0, 0]), random.choice([0, 1]))
    p1_position = (3, 3)
    # Observations
    p0_observation = {
        "my_loc": f"({p0_position[0]}, {p0_position[1]})",
        "opponent_quadrant": "Bottom-Right"
    }
    p1_observation = {
        "my_loc": f"({p1_position[0]}, {p1_position[1]})",
        "opponent_quadrant": "Top-Left"
    }
    return {
        "p0_position": p0_position,
        "p1_position": p1_position,
        "p0_observation": p0_observation,
        "p1_observation": p1_observation
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    p0_position, p1_position = state["p0_position"], state["p1_position"]
    p0_observation, p1_observation = state["p0_observation"], state["p1_observation"]
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        p0_position = (row, col)
        p0_observation["my_loc"] = f"({row}, {col})"
        p0_observation["opponent_quadrant"] = "Top-Left"
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        p1_position = (row, col)
        p1_observation["my_loc"] = f"({row}, {col})"
        p1_observation["opponent_quadrant"] = "Bottom-Right"
    else:
        # Movement actions
        if action == "Up":
            if p0_position[0] > 0:
                p0_position = (p0_position[0] - 1, p0_position[1])
                p0_observation["my_loc"] = f"({p0_position[0]}, {p0_position[1]})"
                p0_observation["opponent_quadrant"] = "Bottom-Right"
            elif p1_position[0] > 0:
                p1_position = (p1_position[0] - 1, p1_position[1])
                p1_observation["my_loc"] = f"({p1_position[0]}, {p1_position[1]})"
                p1_observation["opponent_quadrant"] = "Top-Left"
        elif action == "Down":
            if p0_position[0] < 3:
                p0_position = (p0_position[0] + 1, p0_position[1])
                p0_observation["my_loc"] = f"({p0_position[0]}, {p0_position[1]})"
                p0_observation["opponent_quadrant"] = "Bottom-Right"
            elif p1_position[0] < 3:
                p1_position = (p1_position[0] + 1, p1_position[1])
                p1_observation["my_loc"] = f"({p1_position[0]}, {p1_position[1]})"
                p1_observation["opponent_quadrant"] = "Top-Left"
        elif action == "Left":
            if p0_position[1] > 0:
                p0_position = (p0_position[0], p0_position[1] - 1)
                p0_observation["my_loc"] = f"({p0_position[0]}, {p0_position[1]})"
                p0_observation["opponent_quadrant"] = "Bottom-Right"
            elif p1_position[1] > 0:
                p1_position = (p1_position[0], p1_position[1] - 1)
                p1_observation["my_loc"] = f"({p1_position[0]}, {p1_position[1]})"
                p1_observation["opponent_quadrant"] = "Top-Left"
        elif action == "Right":
            if p0_position[1] < 3:
                p0_position = (p0_position[0], p0_position[1] + 1)
                p0_observation["my_loc"] = f"({p0_position[0]}, {p0_position[1]})"
                p0_observation["opponent_quadrant"] = "Bottom-Right"
            elif p1_position[1] < 3:
                p1_position = (p1_position[0], p1_position[1] + 1)
                p1_observation["my_loc"] = f"({p1_position[0]}, {p1_position[1]})"
                p1_observation["opponent_quadrant"] = "Top-Left"
        elif action == "Stay":
            pass

    return {
        "p0_position": p0_position,
        "p1_position": p1_position,
        "p0_observation": p0_observation,
        "p1_observation": p1_observation
    }

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    p0_position, p1_position = state["p0_position"], state["p1_position"]
    if p0_position == p1_position:
        return -4  # Game over
    else:
        return 0 if p0_position[0] + p0_position[1] % 2 == 0 else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    p0_position, p1_position = state["p0_position"], state["p1_position"]
    if p0_position == p1_position:
        return [-1.0, 1.0]  # Player 0 loses, Player 1 wins
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    p0_position, p1_position = state["p0_position"], state["p1_position"]
    legal_actions = []
    if p0_position != p1_position:
        legal_actions.append("place_p0:<row>,<col>")
        legal_actions.append("place_p1:<row>,<col>")
        if p0_position[0] > 0:
            legal_actions.append("Up")
        if p0_position[0] < 3:
            legal_actions.append("Down")
        if p0_position[1] > 0:
            legal_actions.append("Left")
        if p0_position[1] < 3:
            legal_actions.append("Right")
        legal_actions.append("Stay")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_position, p1_position = state["p0_position"], state["p1_position"]
    p0_observation = {
        "my_loc": f"({p0_position[0]}, {p0_position[1]})",
        "opponent_quadrant": "Bottom-Right" if p0_position[0] + p0_position[1] % 2 == 0 else "Top-Left"
    }
    p1_observation = {
        "my_loc": f"({p1_position[0]}, {p1_position[1]})",
        "opponent_quadrant": "Top-Left" if p1_position[0] + p1_position[1] % 2 == 0 else "Bottom-Right"
    }
    return [p0_observation, p1_observation]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    # This should be replaced with actual resampling logic
    return [
        "place_p0:0,0",
        "Up",
        "Down",
        "Left",
        "Right",
        "Stay"
    ]