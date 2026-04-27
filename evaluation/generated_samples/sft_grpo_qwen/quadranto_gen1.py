import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple, Union

Action = str
State = Dict[str, Union[int, List[int], Dict[str, str]]]
PlayerObservation = Dict[str, Union[str, List[int], Dict[str, str]]]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions
    p0_position = [0, 0]
    p1_position = [3, 3]
    # Observations
    p0_obs = {"loc": "0,0", "opp_quadrant": "Bottom-Right"}
    p1_obs = {"loc": "3,3", "opp_quadrant": "Top-Left"}
    # State dictionary
    state = {
        "p0_position": p0_position,
        "p1_position": p1_position,
        "p0_obs": p0_obs,
        "p1_obs": p1_obs,
        "turn_count": 0,
        "current_player": 0,
        "legal_actions": ["Up", "Down", "Left", "Right", "Stay"]
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    # Update player positions based on action
    if action == "Up":
        new_state["p0_position"][1] -= 1
        new_state["p1_position"][1] -= 1
    elif action == "Down":
        new_state["p0_position"][1] += 1
        new_state["p1_position"][1] += 1
    elif action == "Left":
        new_state["p0_position"][0] -= 1
        new_state["p1_position"][0] -= 1
    elif action == "Right":
        new_state["p0_position"][0] += 1
        new_state["p1_position"][0] += 1
    elif action == "Stay":
        pass
    else:
        raise ValueError("Invalid action")
    
    # Update observations
    p0_obs = new_state["p0_obs"].copy()
    p1_obs = new_state["p1_obs"].copy()
    p0_obs["loc"] = f"{new_state['p0_position'][0]},{new_state['p0_position'][1]}"
    p1_obs["loc"] = f"{new_state['p1_position'][0]},{new_state['p1_position'][1]}"
    p0_obs["opp_quadrant"] = get_quadrant(new_state["p0_position"])
    p1_obs["opp_quadrant"] = get_quadrant(new_state["p1_position"])
    new_state["p0_obs"] = p0_obs
    new_state["p1_obs"] = p1_obs
    
    # Update turn count and current player
    new_state["turn_count"] += 1
    new_state["current_player"] = (new_state["current_player"] + 1) % 2
    
    return new_state

def get_quadrant(position: List[int]) -> str:
    """Determine the quadrant based on the position."""
    row, col = position
    if row < 2 and col < 2:
        return "Top-Left"
    elif row < 2 and col >= 2:
        return "Top-Right"
    elif row >= 2 and col < 2:
        return "Bottom-Left"
    else:
        return "Bottom-Right"

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    p0_position = state["p0_position"]
    p1_position = state["p1_position"]
    if p0_position == p1_position:
        return [-1.0, 1.0]
    elif state["turn_count"] >= 20:
        return [0.0, 0.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    if current_player == -4:
        return []
    else:
        return state["legal_actions"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_position = state["p0_position"]
    p1_position = state["p1_position"]
    p0_obs = {
        "loc": f"{p0_position[0]},{p0_position[1]}",
        "opp_quadrant": get_quadrant(p1_position)
    }
    p1_obs = {
        "loc": f"{p1_position[0]},{p1_position[1]}",
        "opp_quadrant": get_quadrant(p0_position)
    }
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # This function should be implemented to generate a valid sequence of actions
    # that explains the current observations. It should return a list of actions
    # that can be replayed starting from get_initial_state().
    # For simplicity, we'll just return a random valid action sequence.
    legal_actions = get_legal_actions(get_initial_state())
    return [random.choice(legal_actions) for _ in range(len(obs_action_history))]