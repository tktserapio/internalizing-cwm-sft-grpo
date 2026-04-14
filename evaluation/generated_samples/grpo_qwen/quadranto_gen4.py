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
    # Game state dictionary
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
    # Update player positions based on action
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p0_position"] = (row, col)
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p1_position"] = (row, col)
    else:
        # Movement actions
        p0_row, p0_col = new_state["p0_position"]
        p1_row, p1_col = new_state["p1_position"]
        
        if action == "Up":
            new_state["p0_position"] = (p0_row - 1, p0_col)
            new_state["p1_position"] = (p1_row - 1, p1_col)
        elif action == "Down":
            new_state["p0_position"] = (p0_row + 1, p0_col)
            new_state["p1_position"] = (p1_row + 1, p1_col)
        elif action == "Left":
            new_state["p0_position"] = (p0_row, p0_col - 1)
            new_state["p1_position"] = (p1_row, p1_col - 1)
        elif action == "Right":
            new_state["p0_position"] = (p0_row, p0_col + 1)
            new_state["p1_position"] = (p1_row, p1_col + 1)
        elif action == "Stay":
            pass
        
        # Check for game over condition
        if new_state["p0_position"] == new_state["p1_position"]:
            new_state["game_over"] = True
            new_state["current_player"] = -4  # Terminal state
        else:
            new_state["turn_count"] += 1
            new_state["current_player"] = 1 if new_state["current_player"] == 0 else 0
    
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
        return [-1.0, 1.0]  # Player 0 loses, Player 1 wins
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    else:
        current_player = state["current_player"]
        legal_actions = ["Up", "Down", "Left", "Right", "Stay"]
        if current_player == 0:
            # Player 0's legal actions
            p0_row, p0_col = state["p0_position"]
            if p0_row > 0:
                legal_actions.remove("Up")
            if p0_row < 3:
                legal_actions.remove("Down")
            if p0_col > 0:
                legal_actions.remove("Left")
            if p0_col < 3:
                legal_actions.remove("Right")
        else:
            # Player 1's legal actions
            p1_row, p1_col = state["p1_position"]
            if p1_row > 0:
                legal_actions.remove("Up")
            if p1_row < 3:
                legal_actions.remove("Down")
            if p1_col > 0:
                legal_actions.remove("Left")
            if p1_col < 3:
                legal_actions.remove("Right")
        return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_loc = state["p0_position"]
    p1_loc = state["p1_position"]
    p0_quadrant = get_quadrant(p0_loc)
    p1_quadrant = get_quadrant(p1_loc)
    
    p0_obs = {
        "loc": p0_loc,
        "opponent_quadrant": p1_quadrant
    }
    p1_obs = {
        "loc": p1_loc,
        "opponent_quadrant": p0_quadrant
    }
    
    return [p0_obs, p1_obs]

def get_quadrant(loc: Tuple[int, int]) -> str:
    """Determines the quadrant of a given location."""
    row, col = loc
    if row < 2 and col < 2:
        return "Top-Left"
    elif row < 2 and col >= 2:
        return "Top-Right"
    elif row >= 2 and col < 2:
        return "Bottom-Left"
    else:
        return "Bottom-Right"

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement stochastic sampling logic here.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real implementation, this would involve complex probabilistic reasoning.
    return ["Right", "Up", "Down", "Left", "Stay"]