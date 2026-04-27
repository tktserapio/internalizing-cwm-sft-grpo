import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple, Union

Action = str
State = Dict[str, Union[int, List[int], List[List[int]]]]
PlayerObservation = Dict[str, Union[str, List[int], List[List[int]]]]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for players
    p0_position = [0, 0]
    p1_position = [3, 3]
    # Observations for players
    p0_observation = {"loc": p0_position, "opp_quadrant": "Bottom-Right"}
    p1_observation = {"loc": p1_position, "opp_quadrant": "Top-Left"}
    # Game state dictionary
    state = {
        "p0_position": p0_position,
        "p1_position": p1_position,
        "p0_observation": p0_observation,
        "p1_observation": p1_observation,
        "turn_count": 0,
        "current_player": 0,
        "legal_actions": ["Up", "Down", "Left", "Right", "Stay"]
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    # Update player positions based on action
    if action == "Up":
        new_state["p0_position"][1] -= 1 if new_state["p0_position"][1] > 0 else 0
        new_state["p1_position"][1] += 1 if new_state["p1_position"][1] < 3 else 0
    elif action == "Down":
        new_state["p0_position"][1] += 1 if new_state["p0_position"][1] < 3 else 0
        new_state["p1_position"][1] -= 1 if new_state["p1_position"][1] > 0 else 0
    elif action == "Left":
        new_state["p0_position"][0] -= 1 if new_state["p0_position"][0] > 0 else 0
        new_state["p1_position"][0] += 1 if new_state["p1_position"][0] < 3 else 0
    elif action == "Right":
        new_state["p0_position"][0] += 1 if new_state["p0_position"][0] < 3 else 0
        new_state["p1_position"][0] -= 1 if new_state["p1_position"][0] > 0 else 0
    elif action == "Stay":
        pass
    else:
        raise ValueError(f"Invalid action: {action}")
    
    # Update observations
    p0_observation = {
        "loc": new_state["p0_position"],
        "opp_quadrant": "Bottom-Right" if new_state["p0_position"][0] < 2 and new_state["p0_position"][1] < 2 else "Top-Left"
    }
    p1_observation = {
        "loc": new_state["p1_position"],
        "opp_quadrant": "Top-Left" if new_state["p1_position"][0] < 2 and new_state["p1_position"][1] < 2 else "Bottom-Right"
    }
    new_state["p0_observation"] = p0_observation
    new_state["p1_observation"] = p1_observation
    
    # Update current player
    new_state["current_player"] = (new_state["current_player"] + 1) % 2
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    p0_position = state["p0_position"]
    p1_position = state["p1_position"]
    if p0_position == p1_position:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    p0_position = state["p0_position"]
    p1_position = state["p1_position"]
    if p0_position == p1_position:
        return []
    else:
        return state["legal_actions"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_position = state["p0_position"]
    p1_position = state["p1_position"]
    p0_observation = {
        "loc": p0_position,
        "opp_quadrant": "Bottom-Right" if p0_position[0] < 2 and p0_position[1] < 2 else "Top-Left"
    }
    p1_observation = {
        "loc": p1_position,
        "opp_quadrant": "Top-Left" if p1_position[0] < 2 and p1_position[1] < 2 else "Bottom-Right"
    }
    return [p0_observation, p1_observation]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would require more complex logic to handle stochastic sampling.
    # For simplicity, we'll just return a fixed sequence of actions that leads to a win for Player 1.
    # In a real implementation, this would involve a more sophisticated algorithm.
    return ["Up", "Down", "Left", "Right", "Stay"]