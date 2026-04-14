import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to parse the action string
def parse_action(action_str: Action) -> Tuple[int, int, int, int]:
    parts = action_str.split(" to ")
    start = tuple(map(int, parts[0].split(",")))
    end = tuple(map(int, parts[1].split(",")))
    return start, end

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for Blue and Red players
    blue_units = [(0, 0), (0, 4)]
    red_units = [(4, 0), (4, 4)]
    # Game state dictionary
    state = {
        "blue_units": blue_units,
        "red_units": red_units,
        "current_player": 0,
        "turn_count": 0,
        "center_square_occupied": False
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    parsed_action = parse_action(action)
    start, end = parsed_action
    
    # Check if the action is a valid move
    if not (0 <= start[0] < 5 and 0 <= start[1] < 5 and 0 <= end[0] < 5 and 0 <= end[1] < 5):
        raise ValueError("Invalid move coordinates")
    
    # Apply the move
    if start == end:
        raise ValueError("Cannot move to the same position")
    
    # Check if the destination is the center square
    if end == (2, 2):
        state["center_square_occupied"] = True
        return state
    
    # Check if the destination is adjacent to an opponent's unit
    opponent_units = state["red_units" if state["current_player"] == 0 else "blue_units"]
    for opponent_unit in opponent_units:
        if abs(opponent_unit[0] - end[0]) + abs(opponent_unit[1] - end[1]) == 1:
            state["red_units" if state["current_player"] == 0 else "blue_units"].remove(opponent_unit)
            state["red_units" if state["current_player"] == 1 else "blue_units"].append(end)
            state["current_player"] = 1 - state["current_player"]
            state["turn_count"] += 1
            return state
    
    # Check if the destination is adjacent to an opponent's stunned unit
    for opponent_unit in opponent_units:
        if abs(opponent_unit[0] - end[0]) + abs(opponent_unit[1] - end[1]) == 1:
            state["red_units" if state["current_player"] == 0 else "blue_units"].remove(opponent_unit)
            state["red_units" if state["current_player"] == 1 else "blue_units"].append(end)
            state["current_player"] = 1 - state["current_player"]
            state["turn_count"] += 1
            return state
    
    # Check if the destination is adjacent to an opponent's unit that is not stunned
    for opponent_unit in opponent_units:
        if abs(opponent_unit[0] - end[0]) + abs(opponent_unit[1] - end[1]) == 1:
            state["red_units" if state["current_player"] == 0 else "blue_units"].remove(opponent_unit)
            state["red_units" if state["current_player"] == 1 else "blue_units"].append(end)
            state["current_player"] = 1 - state["current_player"]
            state["turn_count"] += 1
            return state
    
    # If no legal moves, pass the turn
    state["current_player"] = 1 - state["current_player"]
    state["turn_count"] += 1
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Blue" if player_id == 0 else "Red"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["center_square_occupied"]:
        return [1.0, 0.0] if state["current_player"] == 0 else [0.0, 1.0]
    elif state["turn_count"] >= 50:
        return [0.5, 0.5]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    if state["current_player"] == 0:
        blue_units = state["blue_units"]
        for unit in blue_units:
            for i in range(5):
                for j in range(5):
                    if (i, j) != unit and (abs(i - unit[0]) + abs(j - unit[1]) <= 1):
                        legal_actions.append(f"move {unit} to {(i, j)}")
    else:
        red_units = state["red_units"]
        for unit in red_units:
            for i in range(5):
                for j in range(5):
                    if (i, j) != unit and (abs(i - unit[0]) + abs(j - unit[1]) <= 1):
                        legal_actions.append(f"move {unit} to {(i, j)}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    blue_units = state["blue_units"]
    red_units = state["red_units"]
    player_0_obs = {"units": blue_units, "opponent_units": red_units}
    player_1_obs = {"units": red_units, "opponent_units": blue_units}
    return [player_0_obs, player_1_obs]