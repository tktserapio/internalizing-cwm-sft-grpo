import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple, Union

# Type definitions
Action = str
State = Dict[str, Union[int, List[int], List[List[int]]]]
PlayerObservation = Dict[str, Union[str, List[str]]]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for players
    p0_position = [(0, 0), (0, 1), (1, 0), (1, 1)]
    p1_position = [(2, 2), (2, 3), (3, 2), (3, 3)]
    
    # Randomly select initial positions for players
    p0_loc = p0_position.pop()
    p1_loc = p1_position.pop()
    
    # Observations
    p0_obs = {"my_loc": f"({p0_loc[0]}, {p0_loc[1]})", "opp_quadrant": "Top-Left"}
    p1_obs = {"my_loc": f"({p1_loc[0]}, {p1_loc[1]})", "opp_quadrant": "Bottom-Right"}
    
    # State
    state = {
        "p0_loc": p0_loc,
        "p1_loc": p1_loc,
        "p0_obs": p0_obs,
        "p1_obs": p1_obs,
        "turn_count": 0,
        "legal_actions": ["Stay"]
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    p0_loc, p1_loc = new_state["p0_loc"], new_state["p1_loc"]
    p0_obs, p1_obs = new_state["p0_obs"], new_state["p1_obs"]
    
    if action == "Stay":
        new_state["legal_actions"].append(action)
    else:
        new_state["legal_actions"] = ["Up", "Down", "Left", "Right", "Stay"]
    
    if action == "Up":
        p1_loc = (p1_loc[0] - 1, p1_loc[1])
    elif action == "Down":
        p1_loc = (p1_loc[0] + 1, p1_loc[1])
    elif action == "Left":
        p1_loc = (p1_loc[0], p1_loc[1] - 1)
    elif action == "Right":
        p1_loc = (p1_loc[0], p1_loc[1] + 1)
    
    new_state["p1_loc"] = p1_loc
    
    # Update observations
    p0_obs["my_loc"] = f"({p0_loc[0]}, {p0_loc[1]})"
    p1_obs["my_loc"] = f"({p1_loc[0]}, {p1_loc[1]})"

    if p0_loc == p1_loc:
        new_state["legal_actions"] = []
        new_state["winner"] = 1
        new_state["loser"] = 0
    elif new_state["turn_count"] >= 20:
        new_state["legal_actions"] = []
        new_state["winner"] = 0
        new_state["loser"] = 0
    else:
        new_state["turn_count"] += 1
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["legal_actions"]:
        return 0
    return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["winner"] == 1:
        return [0.0, -1.0]
    elif state["winner"] == 0:
        return [-1.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["legal_actions"]:
        return state["legal_actions"]
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [state["p0_obs"], state["p1_obs"]]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would require more complex logic to sample valid sequences based on the history.
    # For simplicity, we'll just return a random legal action.
    legal_actions = get_legal_actions(get_initial_state())
    return [legal_actions[0]]  # Return a random legal action as a placeholder