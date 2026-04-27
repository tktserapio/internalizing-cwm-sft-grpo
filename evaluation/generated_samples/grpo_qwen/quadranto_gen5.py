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
    initial_positions = {
        "p0": {"row": 0, "col": 0},
        "p1": {"row": 3, "col": 3}
    }
    # Observations for players
    observations = [
        {"loc": f"({initial_positions['p0']['row']}, {initial_positions['p0']['col']}), Quadrant: Top-Left"},
        {"loc": f"({initial_positions['p1']['row']}, {initial_positions['p1']['col']}), Quadrant: Bottom-Right"}
    ]
    return {
        "state": "setup",
        "players": {
            "p0": initial_positions["p0"],
            "p1": initial_positions["p1"]
        },
        "observations": observations,
        "turn_count": 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = "p0" if state["current_player"] == 0 else "p1"
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["players"][player_id]["row"] = row
        new_state["players"][player_id]["col"] = col
        new_state["observations"][0]["loc"] = f"({row}, {col}), Quadrant: Top-Left"
        new_state["turn_count"] += 1
        new_state["current_player"] = 1
        return new_state
    
    if action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["players"][player_id]["row"] = row
        new_state["players"][player_id]["col"] = col
        new_state["observations"][1]["loc"] = f"({row}, {col}), Quadrant: Bottom-Right"
        new_state["turn_count"] += 1
        new_state["current_player"] = 0
        return new_state
    
    if action in ["Up", "Down", "Left", "Right", "Stay"]:
        player = state["players"][player_id]
        row, col = player["row"], player["col"]
        
        if action == "Up":
            row -= 1
        elif action == "Down":
            row += 1
        elif action == "Left":
            col -= 1
        elif action == "Right":
            col += 1
        elif action == "Stay":
            pass
        
        if 0 <= row < 4 and 0 <= col < 4:
            player["row"], player["col"] = row, col
            new_state["observations"][int(player_id == "p0")]["loc"] = f"({row}, {col}), Quadrant: Top-Left" if player_id == "p0" else f"({row}, {col}), Quadrant: Bottom-Right"
            new_state["turn_count"] += 1
            new_state["current_player"] = 1 if player_id == "p0" else 0
            return new_state
        else:
            raise ValueError("Invalid move: out of bounds")
    
    raise ValueError(f"Unknown action: {action}")

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["turn_count"] >= 20:
        return [0.0, 0.0]
    elif state["current_player"] == 1:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["turn_count"] >= 20:
        return []
    elif state["current_player"] == 0:
        return ["Up", "Down", "Left", "Right", "Stay"]
    else:
        return ["place_p1:<row>,<col>"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_loc = f"({state['players']['p0']['row']}, {state['players']['p0']['col']})"
    p1_loc = f"({state['players']['p1']['row']}, {state['players']['p1']['col']})"
    p0_quadrant = "Top-Left" if state["players"]["p0"]["row"] < 2 and state["players"]["p0"]["col"] < 2 else "Top-Right"
    p1_quadrant = "Bottom-Right" if state["players"]["p1"]["row"] > 1 and state["players"]["p1"]["col"] > 1 else "Bottom-Left"
    return [
        {"loc": p0_loc, "opponent_quadrant": p1_quadrant},
        {"loc": p1_loc, "opponent_quadrant": p0_quadrant}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This is a placeholder function. In a real implementation, this would involve sampling actions based on the observations.
    # For simplicity, we'll just return a fixed sequence of actions that lead to a win for player_id.
    if player_id == 0:
        return ["place_p0:0,0", "Up", "Right", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay"]
    else:
        return ["place_p1:3,3", "Down", "Left", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay", "Stay"]