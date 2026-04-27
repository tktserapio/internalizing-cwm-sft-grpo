import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def place_p0(row: int, col: int) -> Action:
    return f"place_p0:{row},{col}"

def place_p1(row: int, col: int) -> Action:
    return f"place_p1:{row},{col}"

def get_quadrant(loc: Tuple[int, int]) -> str:
    row, col = loc
    if row == 0 and col == 0:
        return "Q1"
    elif row == 0 and col == 3:
        return "Q2"
    elif row == 3 and col == 0:
        return "Q3"
    elif row == 3 and col == 3:
        return "Q4"
    else:
        raise ValueError("Invalid location")

def get_opponent_quadrant(current_quadrant: str) -> str:
    if current_quadrant == "Q1":
        return "Q4"
    elif current_quadrant == "Q2":
        return "Q1"
    elif current_quadrant == "Q3":
        return "Q2"
    elif current_quadrant == "Q4":
        return "Q3"
    else:
        raise ValueError("Invalid quadrant")

def get_random_start_location(quadrant: str) -> Tuple[int, int]:
    if quadrant == "Q1":
        return (0, 0)
    elif quadrant == "Q2":
        return (0, 3)
    elif quadrant == "Q3":
        return (3, 0)
    elif quadrant == "Q4":
        return (3, 3)
    else:
        raise ValueError("Invalid quadrant")

def get_initial_state() -> State:
    p0_loc = get_random_start_location("Q1")
    p1_loc = get_random_start_location("Q4")
    return {
        "p0_loc": p0_loc,
        "p1_loc": p1_loc,
        "current_player": 0,
        "turn_count": 0,
        "legal_actions": ["Stay"]
    }

def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Stay":
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        new_state["legal_actions"] = ["Up", "Down", "Left", "Right", "Stay"]
    else:
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        new_state["legal_actions"] = ["Up", "Down", "Left", "Right", "Stay"]
        new_state["turn_count"] += 1
        new_state["p0_loc"], new_state["p1_loc"] = apply_movement(new_state["p0_loc"], new_state["p1_loc"], action)
    return new_state

def apply_movement(p0_loc: Tuple[int, int], p1_loc: Tuple[int, int], action: Action) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    if action == "Up":
        p0_loc = (p0_loc[0] - 1, p0_loc[1])
        p1_loc = (p1_loc[0] - 1, p1_loc[1])
    elif action == "Down":
        p0_loc = (p0_loc[0] + 1, p0_loc[1])
        p1_loc = (p1_loc[0] + 1, p1_loc[1])
    elif action == "Left":
        p0_loc = (p0_loc[0], p0_loc[1] - 1)
        p1_loc = (p1_loc[0], p1_loc[1] - 1)
    elif action == "Right":
        p0_loc = (p0_loc[0], p0_loc[1] + 1)
        p1_loc = (p1_loc[0], p1_loc[1] + 1)
    elif action == "Stay":
        pass
    else:
        raise ValueError("Invalid action")
    return p0_loc, p1_loc

def get_current_player(state: State) -> int:
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> List[float]:
    p0_loc = state["p0_loc"]
    p1_loc = state["p1_loc"]
    if p0_loc == p1_loc:
        return [-1.0, 1.0]
    elif state["turn_count"] >= 20:
        return [0.0, 0.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    p0_loc = state["p0_loc"]
    p1_loc = state["p1_loc"]
    current_quadrant = get_quadrant(p0_loc)
    opponent_quadrant = get_opponent_quadrant(current_quadrant)
    opponent_loc = state[f"p{1-state['current_player']}_loc"]
    opponent_quadrant_obs = get_quadrant(opponent_loc)
    observations = [
        {"My Loc": f"{p0_loc}", "Opponent Quadrant": opponent_quadrant},
        {"My Loc": f"{p1_loc}", "Opponent Quadrant": opponent_quadrant_obs}
    ]
    return observations

def get_observations(state: State) -> List[PlayerObservation]:
    return get_legal_actions(state)

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would need to be implemented to generate a stochastic sequence of actions based on the observed history.
    # For simplicity, we'll just return a fixed sequence of actions here.
    # In a real implementation, this function would be more complex and stochastic.
    return ["Right", "Up", "Down", "Left", "Stay"]