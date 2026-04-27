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

    # Check if the source and destination are within the board bounds
    if not (0 <= src_row < 5 and 0 <= src_col < 5 and 0 <= dst_row < 5 and 0 <= dst_col < 5):
        return False

    # Check if the source and destination squares are empty
    if state.get(f"{src_row},{src_col}") != "empty":
        return False

    # Check if the destination square is empty
    if state.get(f"{dst_row},{dst_col}") != "empty":
        return False

    return True

def is_adjacent(src: tuple[int, int], dst: tuple[int, int]) -> bool:
    """Check if two squares are adjacent orthogonally or diagonally."""
    return abs(src[0] - dst[0]) + abs(src[1] - dst[1]) == 1

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    state = {
        f"{i},{j}": "empty" for i in range(5) for j in range(5)
    }
    state["0,0"] = "blue"
    state["0,4"] = "blue"
    state["4,0"] = "red"
    state["4,4"] = "red"
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = copy.deepcopy(state)
    src, dst = action.split(" to ")
    src_row, src_col = map(int, src.split(","))
    dst_row, dst_col = map(int, dst.split(","))

    # Apply the move
    new_state[f"{src_row},{src_col}"] = "empty"
    new_state[f"{dst_row},{dst_col}"] = "blue" if state[f"{src_row},{src_col}"] == "blue" else "red"

    # Check for stun
    for player, color in [("blue", "blue"), ("red", "red")]:
        for src, dst in [(src_row, src_col), (dst_row, dst_col)]:
            if state.get(f"{src},{dst}") == color:
                new_state[f"{src},{dst}"] = f"{color}_stunned"

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    blue_units = sum(1 for pos in state.values() if pos == "blue")
    red_units = sum(1 for pos in state.values() if pos == "red")

    if "blue_stunned" in state.values():
        return 0
    elif "red_stunned" in state.values():
        return 1
    elif blue_units > 0 and red_units > 0:
        return -1  # Both players have units
    elif blue_units > 0:
        return 0
    elif red_units > 0:
        return 1
    else:
        return -4  # Draw or end game

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return ["Blue", "Red"][player_id]

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    blue_units = sum(1 for pos in state.values() if pos == "blue")
    red_units = sum(1 for pos in state.values() if pos == "red")

    if state.get("2,2") == "blue":
        return [1.0, 0.0]
    elif state.get("2,2") == "red":
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for player in ["blue", "red"]:
        for unit_pos in state.keys():
            if state[unit_pos] == player:
                for dest_row in range(5):
                    for dest_col in range(5):
                        if state.get(f"{dest_row},{dest_col}") == "empty":
                            action = f"move {unit_pos} to {dest_row},{dest_col}"
                            if is_valid_move(action, state):
                                legal_actions.append(action)

    # Check for stun
    for player, color in [("blue", "blue"), ("red", "red")]:
        for src, dst in [(src_row, src_col), (dst_row, dst_col)]:
            if state.get(f"{src},{dst}") == color:
                legal_actions.append(f"move {src_row},{src_col} to {dst_row},{dst_col}")

    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {}
    player_1_obs = {}

    for row in range(5):
        for col in range(5):
            player_0_obs[f"{row},{col}"] = state.get(f"{row},{col}")
            player_1_obs[f"{row},{col}"] = state.get(f"{row},{col}")

    return [player_0_obs, player_1_obs]