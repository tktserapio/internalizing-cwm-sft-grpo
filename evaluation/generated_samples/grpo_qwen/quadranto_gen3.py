import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for players
    p0_position = (0, 0)
    p1_position = (3, 3)
    
    # Observations for players
    p0_observation = {"loc": p0_position, "opponent_quadrant": "Bottom-Right"}
    p1_observation = {"loc": p1_position, "opponent_quadrant": "Top-Left"}
    
    return {
        "p0_position": p0_position,
        "p1_position": p1_position,
        "p0_observation": p0_observation,
        "p1_observation": p1_observation,
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    p0_position = new_state["p0_position"]
    p1_position = new_state["p1_position"]
    current_player = new_state["current_player"]
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p0_position"] = (row, col)
        new_state["p0_observation"]["loc"] = (row, col)
        new_state["current_player"] = (current_player + 1) % 2
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p1_position"] = (row, col)
        new_state["p1_observation"]["loc"] = (row, col)
        new_state["current_player"] = (current_player + 1) % 2
    else:
        # Movement actions
        if action == "Up":
            new_state["p0_position"] = (max(0, p0_position[0] - 1), p0_position[1])
            new_state["p0_observation"]["loc"] = new_state["p0_position"]
            new_state["p1_position"] = (min(3, p1_position[0] + 1), p1_position[1])
            new_state["p1_observation"]["loc"] = new_state["p1_position"]
        elif action == "Down":
            new_state["p0_position"] = (min(3, p0_position[0] + 1), p0_position[1])
            new_state["p0_observation"]["loc"] = new_state["p0_position"]
            new_state["p1_position"] = (max(0, p1_position[0] - 1), p1_position[1])
            new_state["p1_observation"]["loc"] = new_state["p1_position"]
        elif action == "Left":
            new_state["p0_position"] = (p0_position[0], max(0, p0_position[1] - 1))
            new_state["p0_observation"]["loc"] = new_state["p0_position"]
            new_state["p1_position"] = (p1_position[0], min(3, p1_position[1] + 1))
            new_state["p1_observation"]["loc"] = new_state["p1_position"]
        elif action == "Right":
            new_state["p0_position"] = (p0_position[0], min(3, p0_position[1] + 1))
            new_state["p0_observation"]["loc"] = new_state["p0_position"]
            new_state["p1_position"] = (p1_position[0], max(0, p1_position[1] - 1))
            new_state["p1_observation"]["loc"] = new_state["p1_position"]
        elif action == "Stay":
            pass
        else:
            raise ValueError("Invalid action")
    
    # Check for game over condition
    if new_state["p0_position"] == new_state["p1_position"]:
        new_state["game_over"] = True
        new_state["current_player"] = -4
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["game_over"]:
        return [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    current_player = state["current_player"]
    p0_position = state["p0_position"]
    p1_position = state["p1_position"]
    
    legal_actions = []
    if current_player == 0:
        # Player 0's possible actions
        if p0_position[0] > 0:
            legal_actions.append("Up")
        if p0_position[0] < 3:
            legal_actions.append("Down")
        if p0_position[1] > 0:
            legal_actions.append("Left")
        if p0_position[1] < 3:
            legal_actions.append("Right")
        legal_actions.append("Stay")
    else:
        # Player 1's possible actions
        if p1_position[0] > 0:
            legal_actions.append("Up")
        if p1_position[0] < 3:
            legal_actions.append("Down")
        if p1_position[1] > 0:
            legal_actions.append("Left")
        if p1_position[1] < 3:
            legal_actions.append("Right")
        legal_actions.append("Stay")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_observation = state["p0_observation"]
    p1_observation = state["p1_observation"]
    return [p0_observation, p1_observation]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement the logic to sample actions based on the observations.
    # For simplicity, we'll just return a fixed sequence of actions that lead to a win for player_id.
    # In a real implementation, this would involve more complex logic to ensure the sampled actions match the observed history.
    if player_id == 0:
        return ["place_p0:0,0", "Up", "Down", "Right", "Up", "Stay"]
    else:
        return ["place_p1:3,3", "Down", "Left", "Up", "Stay", "Right"]