import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def is_valid_move(action: Action, state: State) -> bool:
    """Check if the given action is valid based on the current state."""
    # Extract source and destination coordinates from the action string
    src, dst = action.split(" to ")
    src_row, src_col = map(int, src.split(","))
    dst_row, dst_col = map(int, dst.split(","))

    # Check if the source and destination are within the board boundaries
    if not (0 <= src_row < 5 and 0 <= src_col < 5 and 0 <= dst_row < 5 and 0 <= dst_col < 5):
        return False

    # Check if the source and destination squares are empty
    if state.get(f"{src_row},{src_col}") != "0" and state.get(f"{dst_row},{dst_col}") != "0":
        return False

    # Check if the destination square is adjacent to an opponent's unit
    opponent_units = [f"{opp_row},{opp_col}" for opp_row, opp_col in state if state[f"{opp_row},{opp_col}"] == "1"]
    for opp_unit in opponent_units:
        opp_row, opp_col = map(int, opp_unit.split(","))
        if abs(src_row - opp_row) + abs(src_col - opp_col) == 1:
            return True

    return False

def apply_action(state: State, action: Action) -> State:
    """Apply the given action to the current state and return the new state."""
    new_state = copy.deepcopy(state)
    src, dst = action.split(" to ")
    src_row, src_col = map(int, src.split(","))
    dst_row, dst_col = map(int, dst.split(","))

    # Update the source square with an empty space
    new_state[f"{src_row},{src_col}"] = "0"

    # Update the destination square with the unit's value
    new_state[f"{dst_row},{dst_col}"] = new_state[src_row, src_col]

    # Remove the unit from its original position
    del new_state[f"{src_row},{src_col}"]

    # Apply stun mechanic if applicable
    opponent_units = [f"{opp_row},{opp_col}" for opp_row, opp_col in new_state if new_state[f"{opp_row},{opp_col}"] == "1"]
    for opp_unit in opponent_units:
        opp_row, opp_col = map(int, opp_unit.split(","))
        if abs(src_row - opp_row) + abs(src_col - opp_col) == 1:
            new_state[f"{opp_row},{opp_col}"] = "1s"
    
    return new_state

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    initial_state = {
        "0,0": "0", 
        "0,4": "0",
        "1,0": "1",
        "1,4": "1",
        "2,2": "0"
    }
    return initial_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    blue_units = sum(1 for pos in state.values() if pos == "0")
    red_units = sum(1 for pos in state.values() if pos == "1")

    if blue_units > 0:
        return 0
    elif red_units > 0:
        return 1
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return ["Blue", "Red"][player_id]

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    blue_units = sum(1 for pos in state.values() if pos == "0")
    red_units = sum(1 for pos in state.values() if pos == "1")

    if state["2,2"] == "0":
        return [1.0, 0.0]
    elif state["2,2"] == "1s":
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    if current_player == -4:
        return []

    legal_actions = []
    for pos, unit in state.items():
        if unit == str(current_player):
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                row, col = map(int, pos.split(","))
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 5 and 0 <= new_col < 5 and state.get(f"{new_row},{new_col}") == "0":
                    legal_actions.append(f"move {pos} to {new_row},{new_col}")
                elif state.get(f"{new_row},{new_col}") == "1" and is_valid_move(f"move {pos} to {new_row},{new_col}", state):
                    legal_actions.append(f"move {pos} to {new_row},{new_col}")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {}
    player_1_obs = {}

    for pos, unit in state.items():
        row, col = map(int, pos.split(","))
        if unit == "0":
            player_0_obs[pos] = {"unit": "Blue"}
        elif unit == "1":
            player_1_obs[pos] = {"unit": "Red"}

    return [player_0_obs, player_1_obs]