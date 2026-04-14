import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions
    p0_position = (0, 0)  # Player 0 starts at (0,0) in Q1
    p1_position = (3, 3)  # Player 1 starts at (3,3) in Q4
    # Observations
    p0_obs = {"loc": p0_position, "opp_quadrant": "Bottom-Right"}
    p1_obs = {"loc": p1_position, "opp_quadrant": "Top-Left"}
    # State dictionary
    state = {
        "p0_position": p0_position,
        "p1_position": p1_position,
        "p0_obs": p0_obs,
        "p1_obs": p1_obs,
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    p0_position = new_state["p0_position"]
    p1_position = new_state["p1_position"]
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p0_position"] = (row, col)
        new_state["p0_obs"]["loc"] = (row, col)
        new_state["p0_obs"]["opp_quadrant"] = get_quadrant(p1_position)
        new_state["current_player"] = 1
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p1_position"] = (row, col)
        new_state["p1_obs"]["loc"] = (row, col)
        new_state["p1_obs"]["opp_quadrant"] = get_quadrant(p0_position)
        new_state["current_player"] = 0
    else:
        # Movement actions
        if action == "Up":
            if p0_position[1] > 0:
                new_state["p0_position"] = (p0_position[0], p0_position[1] - 1)
                new_state["p0_obs"]["loc"] = (p0_position[0], p0_position[1] - 1)
                new_state["p0_obs"]["opp_quadrant"] = get_quadrant(p1_position)
            else:
                new_state["p0_position"] = p0_position
        elif action == "Down":
            if p0_position[1] < 3:
                new_state["p0_position"] = (p0_position[0], p0_position[1] + 1)
                new_state["p0_obs"]["loc"] = (p0_position[0], p0_position[1] + 1)
                new_state["p0_obs"]["opp_quadrant"] = get_quadrant(p1_position)
            else:
                new_state["p0_position"] = p0_position
        elif action == "Left":
            if p0_position[0] > 0:
                new_state["p0_position"] = (p0_position[0] - 1, p0_position[1])
                new_state["p0_obs"]["loc"] = (p0_position[0] - 1, p0_position[1])
                new_state["p0_obs"]["opp_quadrant"] = get_quadrant(p1_position)
            else:
                new_state["p0_position"] = p0_position
        elif action == "Right":
            if p0_position[0] < 3:
                new_state["p0_position"] = (p0_position[0] + 1, p0_position[1])
                new_state["p0_obs"]["loc"] = (p0_position[0] + 1, p0_position[1])
                new_state["p0_obs"]["opp_quadrant"] = get_quadrant(p1_position)
            else:
                new_state["p0_position"] = p0_position
        elif action == "Stay":
            new_state["p0_position"] = p0_position
        else:
            raise ValueError("Invalid action")
        
        if action != "Stay":
            new_state["current_player"] = 1 - new_state["current_player"]
    
    return new_state

def get_quadrant(position: Tuple[int, int]) -> str:
    """Determine the quadrant based on the position."""
    if position[0] == 0 and position[1] == 0:
        return "Top-Left"
    elif position[0] == 0 and position[1] == 3:
        return "Top-Right"
    elif position[0] == 3 and position[1] == 0:
        return "Bottom-Left"
    elif position[0] == 3 and position[1] == 3:
        return "Bottom-Right"
    else:
        raise ValueError("Position out of bounds")

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["game_over"]:
        winner = 1 if state["current_player"] == 0 else 0
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = state["current_player"]
    if state["game_over"]:
        return []
    else:
        if current_player == 0:
            return ["Up", "Down", "Left", "Right", "Stay"]
        else:
            return ["place_p1:<row>,<col>"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {"loc": state["p0_position"], "opp_quadrant": state["p1_obs"]["opp_quadrant"]},
        {"loc": state["p1_position"], "opp_quadrant": state["p0_obs"]["opp_quadrant"]}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement the logic to sample actions based on the observations.
    # For simplicity, we'll just return a fixed sequence here.
    # In a real implementation, this would involve sampling based on the current state and observations.
    return ["place_p0:0,0", "Up", "Down", "Left", "Right", "Stay"]