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
    # Observations for both players
    p0_observation = {"loc": p0_position, "opp_quadrant": "Bottom-Right"}
    p1_observation = {"loc": p1_position, "opp_quadrant": "Top-Left"}
    # Initial state dictionary
    state = {
        "p0_position": p0_position,
        "p1_position": p1_position,
        "p0_observation": p0_observation,
        "p1_observation": p1_observation,
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
        new_state["p0_observation"]["loc"] = (row, col)
        new_state["current_player"] = 1
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p1_position"] = (row, col)
        new_state["p1_observation"]["loc"] = (row, col)
        new_state["current_player"] = 0
    else:
        # Movement actions
        if action == "Up":
            if p0_position[0] > 0:
                new_state["p0_position"] = (p0_position[0] - 1, p0_position[1])
                new_state["p0_observation"]["loc"] = (p0_position[0] - 1, p0_position[1])
        elif action == "Down":
            if p0_position[0] < 3:
                new_state["p0_position"] = (p0_position[0] + 1, p0_position[1])
                new_state["p0_observation"]["loc"] = (p0_position[0] + 1, p0_position[1])
        elif action == "Left":
            if p0_position[1] > 0:
                new_state["p0_position"] = (p0_position[0], p0_position[1] - 1)
                new_state["p0_observation"]["loc"] = (p0_position[0], p0_position[1] - 1)
        elif action == "Right":
            if p0_position[1] < 3:
                new_state["p0_position"] = (p0_position[0], p0_position[1] + 1)
                new_state["p0_observation"]["loc"] = (p0_position[0], p0_position[1] + 1)
        elif action == "Stay":
            pass
        
        if action == "Up":
            if p1_position[0] > 0:
                new_state["p1_position"] = (p1_position[0] - 1, p1_position[1])
                new_state["p1_observation"]["loc"] = (p1_position[0] - 1, p1_position[1])
        elif action == "Down":
            if p1_position[0] < 3:
                new_state["p1_position"] = (p1_position[0] + 1, p1_position[1])
                new_state["p1_observation"]["loc"] = (p1_position[0] + 1, p1_position[1])
        elif action == "Left":
            if p1_position[1] > 0:
                new_state["p1_position"] = (p1_position[0], p1_position[1] - 1)
                new_state["p1_observation"]["loc"] = (p1_position[0], p1_position[1] - 1)
        elif action == "Right":
            if p1_position[1] < 3:
                new_state["p1_position"] = (p1_position[0], p1_position[1] + 1)
                new_state["p1_observation"]["loc"] = (p1_position[0], p1_position[1] + 1)
        elif action == "Stay":
            pass
    
    # Check if the game is over
    if abs(p0_position[0] - p1_position[0]) + abs(p0_position[1] - p1_position[1]) == 1:
        new_state["game_over"] = True
        new_state["winner"] = 1
        new_state["loser"] = 0
    elif new_state["turn_count"] >= 20:
        new_state["game_over"] = True
        new_state["winner"] = 0
        new_state["loser"] = 1
    else:
        new_state["current_player"] = 1 - new_state["current_player"]
        new_state["turn_count"] += 1
    
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
        winner = state["winner"]
        loser = state["loser"]
        return [1.0 if winner == 1 else -1.0, 1.0 if winner == 0 else -1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    current_player = state["current_player"]
    legal_actions = []
    if current_player == 0:
        legal_actions.append("place_p0:<row>,<col>")
        legal_actions.append("Up")
        legal_actions.append("Down")
        legal_actions.append("Left")
        legal_actions.append("Right")
        legal_actions.append("Stay")
    else:
        legal_actions.append("place_p1:<row>,<col>")
        legal_actions.append("Up")
        legal_actions.append("Down")
        legal_actions.append("Left")
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
    # This function would require more complex logic to handle stochastic sampling based on the observations.
    # For simplicity, we'll just return a fixed sequence of actions that lead to the given observations.
    # In a real implementation, this function would need to account for the stochastic nature of the game.
    # Here, we assume a deterministic sequence that leads to the given observations.
    # Note: This is a placeholder implementation.
    if player_id == 0:
        return ["place_p0:0,0", "Up", "Down", "Right", "Stay", "Up"]
    else:
        return ["place_p1:3,3", "Down", "Up", "Left", "Stay", "Up"]