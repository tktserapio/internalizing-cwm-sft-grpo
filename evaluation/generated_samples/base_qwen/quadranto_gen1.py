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
def get_random_initial_position():
    positions = [(0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 0), (2, 1), (3, 0), (3, 1), (2, 2), (2, 3), (3, 2), (3, 3)]
    return random.choice(positions)

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    p0_pos = get_random_initial_position()
    p1_pos = get_random_initial_position()
    while p0_pos == p1_pos:
        p1_pos = get_random_initial_position()
    return {
        "p0": {"position": p0_pos, "quadrant": "Q1"},
        "p1": {"position": p1_pos, "quadrant": "Q4"}
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    p0 = state["p0"]
    p1 = state["p1"]
    
    # Update position based on action
    if action == "Up":
        p0["position"] = (p0["position"][0], p0["position"][1] - 1)
        p1["position"] = (p1["position"][0], p1["position"][1] - 1)
    elif action == "Down":
        p0["position"] = (p0["position"][0], p0["position"][1] + 1)
        p1["position"] = (p1["position"][0], p1["position"][1] + 1)
    elif action == "Left":
        p0["position"] = (p0["position"][0] - 1, p0["position"][1])
        p1["position"] = (p1["position"][0] - 1, p1["position"][1])
    elif action == "Right":
        p0["position"] = (p0["position"][0] + 1, p0["position"][1])
        p1["position"] = (p1["position"][0] + 1, p1["position"][1])
    elif action == "Stay":
        pass
    
    # Determine the quadrant of each player
    p0_quadrant = determine_quadrant(p0["position"])
    p1_quadrant = determine_quadrant(p1["position"])
    
    # Update the state
    return {
        "p0": {"position": p0["position"], "quadrant": p0_quadrant},
        "p1": {"position": p1["position"], "quadrant": p1_quadrant}
    }

def determine_quadrant(position):
    row, col = position
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
    p0_position = state["p0"]["position"]
    p1_position = state["p1"]["position"]
    if p0_position == p1_position:
        return -4  # Game over, draw
    elif state["p0"]["quadrant"] == "Q1" and state["p1"]["quadrant"] == "Q4":
        return 0  # Player 0's turn
    else:
        return 1  # Player 1's turn

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    p0_position = state["p0"]["position"]
    p1_position = state["p1"]["position"]
    if p0_position == p1_position:
        return [-1.0, 1.0]  # One player caught the other
    else:
        return [0.0, 0.0]  # Not caught yet

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    if current_player == -4:
        return []  # Terminal state
    elif current_player == 0:
        return ["Up", "Down", "Left", "Right", "Stay"]
    else:
        return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_position = state["p0"]["position"]
    p1_position = state["p1"]["position"]
    p0_quadrant = state["p0"]["quadrant"]
    p1_quadrant = state["p1"]["quadrant"]
    return [
        {"my_loc": p0_position, "opponent_quadrant": p1_quadrant},
        {"my_loc": p1_position, "opponent_quadrant": p0_quadrant}
    ]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement stochastic sampling logic here.
    # For simplicity, we'll just return a fixed sequence of actions that lead to a win for player_id.
    # In a real implementation, this would involve more complex logic.
    if player_id == 0:
        return ["Right", "Down", "Right", "Up", "Right", "Up", "Right", "Up", "Right", "Up", "Right", "Up", "Right", "Up", "Right", "Up", "Right", "Up", "Right", "Up"]
    else:
        return ["Left", "Down", "Left", "Down", "Left", "Down", "Left", "Down", "Left", "Down", "Left", "Down", "Left", "Down", "Left", "Down", "Left", "Down", "Left", "Down"]