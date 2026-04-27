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
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial positions for Player 0 and Player 1
    p0_pos = get_random_initial_position()
    p1_pos = get_random_initial_position()
    
    # Mapping of quadrants to coordinates
    quadrant_mapping = {
        "Q1": [(0, 0), (0, 1), (1, 0), (1, 1)],
        "Q2": [(0, 2), (0, 3), (1, 2), (1, 3)],
        "Q3": [(2, 0), (2, 1), (3, 0), (3, 1)],
        "Q4": [(2, 2), (2, 3), (3, 2), (3, 3)]
    }
    
    # Observations
    p0_obs = {"loc": p0_pos, "opp_quadrant": quadrant_mapping["Q4"]}
    p1_obs = {"loc": p1_pos, "opp_quadrant": quadrant_mapping["Q1"]}
    
    return {
        "p0_pos": p0_pos,
        "p1_pos": p1_pos,
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
        new_state["turn_count"] += 1
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        new_state["legal_actions"] = ["Up", "Down", "Left", "Right", "Stay"]
    else:
        new_state["turn_count"] += 1
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        new_state["legal_actions"] = ["Up", "Down", "Left", "Right", "Stay"]
        
        # Update player positions based on the action
        if action == "Up":
            new_state["p0_pos"] = (new_state["p0_pos"][0], max(0, new_state["p0_pos"][1] - 1))
            new_state["p1_pos"] = (new_state["p1_pos"][0], min(3, new_state["p1_pos"][1] + 1))
        elif action == "Down":
            new_state["p0_pos"] = (new_state["p0_pos"][0], min(3, new_state["p0_pos"][1] + 1))
            new_state["p1_pos"] = (new_state["p1_pos"][0], max(0, new_state["p1_pos"][1] - 1))
        elif action == "Left":
            new_state["p0_pos"] = (max(0, new_state["p0_pos"][0] - 1), new_state["p0_pos"][1])
            new_state["p1_pos"] = (min(3, new_state["p1_pos"][0] + 1), new_state["p1_pos"][1])
        elif action == "Right":
            new_state["p0_pos"] = (min(3, new_state["p0_pos"][0] + 1), new_state["p0_pos"][1])
            new_state["p1_pos"] = (max(0, new_state["p1_pos"][0] - 1), new_state["p1_pos"][1])
        else:
            raise ValueError("Invalid action")
        
        # Check if the game is over
        if new_state["p0_pos"] == new_state["p1_pos"]:
            new_state["game_over"] = True
            new_state["winner"] = 1
            new_state["loser"] = 0
            new_state["reward"] = [1.0, -1.0]
        else:
            new_state["game_over"] = False
            new_state["winner"] = 0
            new_state["loser"] = 1
            new_state["reward"] = [-1.0, 1.0]
    
    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state.get("current_player", -4)

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    return state.get("reward", [0.0, 0.0])

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    return state.get("legal_actions", [])

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs].
    """
    return [
        {"loc": state["p0_pos"], "opp_quadrant": state["p1_obs"]["opp_quadrant"]},
        {"loc": state["p1_pos"], "opp_quadrant": state["p0_obs"]["opp_quadrant"]}
    ]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to be implemented based on the specific game dynamics and history data.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real scenario, this function would be more complex and handle the stochastic nature of the game.
    return ["Stay", "Up", "Down", "Left", "Right"]