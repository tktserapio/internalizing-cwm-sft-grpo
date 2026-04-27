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

# Helper function to generate random initial positions
def get_random_position():
    return random.choice([(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)])

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for players
    p0_pos = get_random_position()
    p1_pos = get_random_position()
    while p0_pos == p1_pos:
        p1_pos = get_random_position()
    
    return {
        "p0": p0_pos,
        "p1": p1_pos,
        "turn_count": 0,
        "current_quadrant_p0": None,
        "current_quadrant_p1": None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    p0_loc = new_state["p0"]
    p1_loc = new_state["p1"]
    current_quadrant_p0 = new_state["current_quadrant_p0"]
    current_quadrant_p1 = new_state["current_quadrant_p1"]
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p0"] = (row, col)
        new_state["current_quadrant_p0"] = get_quadrant(row, col)
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p1"] = (row, col)
        new_state["current_quadrant_p1"] = get_quadrant(row, col)
    else:
        if action in ["Up", "Down", "Left", "Right"]:
            if action == "Up":
                p0_loc = (p0_loc[0] - 1, p0_loc[1])
                p1_loc = (p1_loc[0] - 1, p1_loc[1])
            elif action == "Down":
                p0_loc = (p0_loc[0] + 1, p0_loc[1])
                p1_loc = (p1_loc[0] + 1, p1_loc[1])
            elif action == "Left":
                p0_loc = (p0_loc[0], p0_loc[1] - 1)
                p1_loc = (p1_loc[0], p1_loc[1] - 1)
            elif action == "Right":
                p0_loc = (p0_loc[0], p0_loc[1] + 1)
                p1_loc = (p1_loc[0], p1_loc[1] + 1)
        new_state["p0"] = p0_loc
        new_state["p1"] = p1_loc
        new_state["current_quadrant_p0"] = get_quadrant(p0_loc[0], p0_loc[1])
        new_state["current_quadrant_p1"] = get_quadrant(p1_loc[0], p1_loc[1])
    
    new_state["turn_count"] += 1
    return new_state

def get_quadrant(row: int, col: int) -> str:
    """Determine the quadrant based on the row and column."""
    if row < 2 and col < 2:
        return "Q1"
    elif row < 2 and col >= 2:
        return "Q2"
    elif row >= 2 and col < 2:
        return "Q3"
    else:
        return "Q4"

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["turn_count"] < 20:
        return 0 if state["p0"] == state["p1"] else -4
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["turn_count"] < 20:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["turn_count"] >= 20:
        return []
    else:
        p0_loc = state["p0"]
        p1_loc = state["p1"]
        current_quadrant_p0 = state["current_quadrant_p0"]
        current_quadrant_p1 = state["current_quadrant_p1"]
        
        legal_actions_p0 = ["Stay"]
        if current_quadrant_p0 != current_quadrant_p1:
            legal_actions_p0.append("Right")
            legal_actions_p0.append("Left")
            legal_actions_p0.append("Up")
            legal_actions_p0.append("Down")
        
        legal_actions_p1 = ["Stay"]
        if current_quadrant_p0 != current_quadrant_p1:
            legal_actions_p1.append("Right")
            legal_actions_p1.append("Left")
            legal_actions_p1.append("Up")
            legal_actions_p1.append("Down")
        
        return legal_actions_p0 + legal_actions_p1

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_loc = state["p0"]
    p1_loc = state["p1"]
    current_quadrant_p0 = state["current_quadrant_p0"]
    current_quadrant_p1 = state["current_quadrant_p1"]
    
    player_0_obs = {
        "My Loc": f"({p0_loc[0]}, {p0_loc[1]})",
        "Opponent Quadrant": current_quadrant_p1
    }
    player_1_obs = {
        "My Loc": f"({p1_loc[0]}, {p1_loc[1]})",
        "Opponent Quadrant": current_quadrant_p0
    }
    
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This is a placeholder function for demonstration purposes.
    # In a real implementation, this would involve more complex logic.
    return obs_action_history[-1][1]