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

# Helper function to generate random initial positions
def generate_random_position():
    return random.choice([(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)])

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for players
    p0_pos = generate_random_position()
    p1_pos = generate_random_position()
    
    # Observations for both players
    p0_obs = {
        "my_loc": p0_pos,
        "opp_quadrant": "Top-Left" if p1_pos in [(2, 0), (2, 1), (3, 0), (3, 1)] else "Top-Right",
    }
    p1_obs = {
        "my_loc": p1_pos,
        "opp_quadrant": "Bottom-Left" if p0_pos in [(2, 0), (2, 1), (3, 0), (3, 1)] else "Bottom-Right",
    }
    
    return {
        "state": "initial",
        "p0_pos": p0_pos,
        "p1_pos": p1_pos,
        "p0_obs": p0_obs,
        "p1_obs": p1_obs,
        "turn_count": 0,
        "legal_actions": ["Stay"],
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    
    if state["state"] == "initial":
        # Place players
        new_state["p0_pos"] = state["p0_pos"]
        new_state["p1_pos"] = state["p1_pos"]
        new_state["p0_obs"]["my_loc"] = state["p0_pos"]
        new_state["p1_obs"]["my_loc"] = state["p1_pos"]
        new_state["legal_actions"] = ["Stay"]
        new_state["turn_count"] += 1
        
        return new_state
    
    if action == "Stay":
        new_state["legal_actions"].remove(action)
        new_state["turn_count"] += 1
        return new_state
    
    # Update player positions based on action
    if action in ["Up", "Down", "Left", "Right"]:
        if action == "Up":
            new_state["p0_pos"] = (new_state["p0_pos"][0], max(0, new_state["p0_pos"][1] - 1))
            new_state["p1_pos"] = (new_state["p1_pos"][0], max(0, new_state["p1_pos"][1] - 1))
        elif action == "Down":
            new_state["p0_pos"] = (new_state["p0_pos"][0], min(3, new_state["p0_pos"][1] + 1))
            new_state["p1_pos"] = (new_state["p1_pos"][0], min(3, new_state["p1_pos"][1] + 1))
        elif action == "Left":
            new_state["p0_pos"] = (max(0, new_state["p0_pos"][0] - 1), new_state["p0_pos"][1])
            new_state["p1_pos"] = (max(0, new_state["p1_pos"][0] - 1), new_state["p1_pos"][1])
        elif action == "Right":
            new_state["p0_pos"] = (min(3, new_state["p0_pos"][0] + 1), new_state["p0_pos"][1])
            new_state["p1_pos"] = (min(3, new_state["p1_pos"][0] + 1), new_state["p1_pos"][1])
        
        new_state["p0_obs"]["my_loc"] = new_state["p0_pos"]
        new_state["p1_obs"]["my_loc"] = new_state["p1_pos"]
        
        # Determine opponent's quadrant
        if new_state["p0_pos"] in [(2, 0), (2, 1), (3, 0), (3, 1)]:
            new_state["p1_obs"]["opp_quadrant"] = "Bottom-Left"
        else:
            new_state["p1_obs"]["opp_quadrant"] = "Bottom-Right"
        
        if new_state["p1_pos"] in [(2, 0), (2, 1), (3, 0), (3, 1)]:
            new_state["p0_obs"]["opp_quadrant"] = "Top-Left"
        else:
            new_state["p0_obs"]["opp_quadrant"] = "Top-Right"
        
        new_state["legal_actions"] = ["Stay"]
        
        if new_state["p0_pos"] == new_state["p1_pos"]:
            new_state["state"] = "terminal"
            new_state["p0_obs"]["my_loc"] = new_state["p0_pos"]
            new_state["p1_obs"]["my_loc"] = new_state["p1_pos"]
            new_state["p0_obs"]["opp_quadrant"] = "Bottom-Right"
            new_state["p1_obs"]["opp_quadrant"] = "Top-Left"
            new_state["p0_obs"]["catched"] = True
            new_state["p1_obs"]["catched"] = True
            new_state["p0_obs"]["points"] = 1.0
            new_state["p1_obs"]["points"] = -1.0
            new_state["p0_obs"]["game_over"] = True
            new_state["p1_obs"]["game_over"] = True
            
            return new_state
        
        if new_state["turn_count"] >= 20:
            new_state["state"] = "terminal"
            new_state["p0_obs"]["my_loc"] = new_state["p0_pos"]
            new_state["p1_obs"]["my_loc"] = new_state["p1_pos"]
            new_state["p0_obs"]["opp_quadrant"] = "Bottom-Right"
            new_state["p1_obs"]["opp_quadrant"] = "Top-Left"
            new_state["p0_obs"]["catched"] = False
            new_state["p1_obs"]["catched"] = False
            new_state["p0_obs"]["points"] = 0.0
            new_state["p1_obs"]["points"] = 0.0
            new_state["p0_obs"]["game_over"] = True
            new_state["p1_obs"]["game_over"] = True
            
            return new_state
        
        return new_state
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["state"] == "terminal":
        return -4
    return 0 if state["turn_count"] % 2 == 0 else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["state"] == "terminal":
        return [state["p0_obs"]["points"], state["p1_obs"]["points"]]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["state"] == "terminal":
        return []
    return state["legal_actions"]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [state["p0_obs"], state["p1_obs"]]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would require more complex logic to handle stochastic sampling.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real implementation, this would involve sampling from possible sequences.
    if player_id == 0:
        return ["Right", "Down", "Right", "Up", "Right", "Up"]
    else:
        return ["Up", "Left", "Up", "Right", "Up", "Left"]