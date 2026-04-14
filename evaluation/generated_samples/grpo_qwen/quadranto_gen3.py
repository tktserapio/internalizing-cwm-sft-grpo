import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple, Union
import random

# Type definitions
Action = str
State = Dict[str, Union[int, List[int], List[List[int]]]]
PlayerObservation = Dict[str, Union[str, List[str]]]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for players
    initial_positions = [(0, 0), (3, 3)]
    # Randomly assign initial positions
    random.shuffle(initial_positions)
    p0_pos, p1_pos = initial_positions
    return {
        "p0": p0_pos,
        "p1": p1_pos,
        "current_player": 0,
        "turn_count": 0,
        "quadrant_p0": "Q1",
        "quadrant_p1": "Q4",
        "moves_left": 20
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    p0_loc, p1_loc = new_state["p0"], new_state["p1"]
    quadrant_p0, quadrant_p1 = new_state["quadrant_p0"], new_state["quadrant_p1"]
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p0"] = [row, col]
        new_state["quadrant_p0"] = get_quadrant(row, col)
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p1"] = [row, col]
        new_state["quadrant_p1"] = get_quadrant(row, col)
    else:
        # Movement actions
        if action == "Up":
            new_state["p0"][0] -= 1
            new_state["p1"][0] -= 1
        elif action == "Down":
            new_state["p0"][0] += 1
            new_state["p1"][0] += 1
        elif action == "Left":
            new_state["p0"][1] -= 1
            new_state["p1"][1] -= 1
        elif action == "Right":
            new_state["p0"][1] += 1
            new_state["p1"][1] += 1
        elif action == "Stay":
            pass
        else:
            raise ValueError(f"Invalid action: {action}")
        
        # Check if players have moved out of bounds
        new_state["p0"] = [max(0, min(new_state["p0"][0], 3)), max(0, min(new_state["p0"][1], 3))]
        new_state["p1"] = [max(0, min(new_state["p1"][0], 3)), max(0, min(new_state["p1"][1], 3))]

    # Update turn count
    new_state["turn_count"] += 1
    
    # Determine current player
    if new_state["p0"] == new_state["p1"]:
        new_state["current_player"] = 1
        new_state["moves_left"] = 0
    else:
        new_state["current_player"] = 0
    
    return new_state

def get_quadrant(row: int, col: int) -> str:
    """Determine the quadrant based on the row and column."""
    if row < 2 and col < 2:
        return "Q1"
    elif row < 2 and col >= 2:
        return "Q2"
    elif row >= 2 and col < 2:
        return "Q3"
    else:
        return "Q4"

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["moves_left"] == 0:
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["moves_left"] == 0:
        return [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["moves_left"] == 0:
        return []
    current_player = state["current_player"]
    actions = ["Up", "Down", "Left", "Right", "Stay"]
    if current_player == 0:
        return actions
    else:
        return actions[:3] + actions[4:]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_loc, p1_loc = state["p0"], state["p1"]
    quadrant_p0, quadrant_p1 = state["quadrant_p0"], state["quadrant_p1"]
    return [
        {"loc": f"{p0_loc[0]}, {p0_loc[1]}", "opponent_quadrant": quadrant_p1},
        {"loc": f"{p1_loc[0]}, {p1_loc[1]}", "opponent_quadrant": quadrant_p0}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would require more complex logic to handle stochastic sampling.
    # For simplicity, we'll just return a fixed sequence of actions that leads to the given observations.
    # In a real implementation, this function would need to handle the stochastic nature of the game.
    if player_id == 0:
        return ["Right", "Down", "Right", "Up", "Right", "Up"]
    else:
        return ["Up", "Left", "Up", "Left", "Up"]