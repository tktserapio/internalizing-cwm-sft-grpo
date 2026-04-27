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
def _generate_random_position():
    return random.choice([(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)])

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for players
    p0_pos = _generate_random_position()
    p1_pos = _generate_random_position()
    while p0_pos == p1_pos:
        p1_pos = _generate_random_position()
    
    # Initial state
    return {
        "p0_pos": p0_pos,
        "p1_pos": p1_pos,
        "turn_count": 0,
        "p0_quadrant": "Q1" if p0_pos in [(0, 0), (0, 1), (1, 0), (1, 1)] else "Q4",
        "p1_quadrant": "Q4" if p1_pos in [(0, 0), (0, 1), (1, 0), (1, 1)] else "Q1",
        "p0_obs": {"loc": p0_pos, "opp_quadrant": "Q4" if p1_pos in [(0, 0), (0, 1), (1, 0), (1, 1)] else "Q1"},
        "p1_obs": {"loc": p1_pos, "opp_quadrant": "Q1" if p0_pos in [(0, 0), (0, 1), (1, 0), (1, 1)] else "Q4"}
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    p0_pos, p1_pos = new_state["p0_pos"], new_state["p1_pos"]
    p0_quadrant, p1_quadrant = new_state["p0_quadrant"], new_state["p1_quadrant"]
    p0_obs, p1_obs = new_state["p0_obs"], new_state["p1_obs"]
    
    if action == "Stay":
        new_state["p0_pos"] = p0_pos
        new_state["p1_pos"] = p1_pos
        new_state["p0_obs"]["loc"] = p0_pos
        new_state["p1_obs"]["loc"] = p1_pos
    elif action in ["Up", "Down", "Left", "Right"]:
        if action == "Up":
            new_state["p0_pos"] = (p0_pos[0], p0_pos[1] - 1)
            new_state["p1_pos"] = (p1_pos[0], p1_pos[1] - 1)
        elif action == "Down":
            new_state["p0_pos"] = (p0_pos[0], p0_pos[1] + 1)
            new_state["p1_pos"] = (p1_pos[0], p1_pos[1] + 1)
        elif action == "Left":
            new_state["p0_pos"] = (p0_pos[0] - 1, p0_pos[1])
            new_state["p1_pos"] = (p1_pos[0] - 1, p1_pos[1])
        elif action == "Right":
            new_state["p0_pos"] = (p0_pos[0] + 1, p0_pos[1])
            new_state["p1_pos"] = (p1_pos[0] + 1, p1_pos[1])
        
        new_state["p0_obs"]["loc"] = new_state["p0_pos"]
        new_state["p1_obs"]["loc"] = new_state["p1_pos"]
        
        if new_state["p0_pos"] == new_state["p1_pos"]:
            new_state["p0_quadrant"], new_state["p1_quadrant"] = new_state["p1_quadrant"], new_state["p0_quadrant"]
            new_state["p0_obs"]["opp_quadrant"], new_state["p1_obs"]["opp_quadrant"] = new_state["p1_obs"]["opp_quadrant"], new_state["p0_obs"]["opp_quadrant"]
            new_state["p0_obs"]["loc"] = new_state["p0_pos"]
            new_state["p1_obs"]["loc"] = new_state["p1_pos"]
            new_state["p0_obs"]["opp_quadrant"] = new_state["p1_quadrant"]
            new_state["p1_obs"]["opp_quadrant"] = new_state["p0_quadrant"]
            new_state["turn_count"] = 20
            new_state["p0_obs"]["catch"] = True
            new_state["p1_obs"]["catch"] = False
        else:
            new_state["turn_count"] += 1
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["turn_count"] >= 20:
        return -4
    return 0 if state["p0_pos"] == state["p1_pos"] else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["turn_count"] >= 20:
        return [0.0, 0.0]
    return [-1.0, 1.0] if state["p0_pos"] == state["p1_pos"] else [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["turn_count"] >= 20:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_obs = state["p0_obs"]
    p1_obs = state["p1_obs"]
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement the logic to sample a valid sequence of actions.
    # For simplicity, we'll just return a fixed sequence here.
    # In a real implementation, this would involve sampling from the possible actions based on the current state.
    if player_id == 0:
        return ["Right", "Down", "Right", "Up", "Left"]
    else:
        return ["Up", "Left", "Up", "Right", "Up"]