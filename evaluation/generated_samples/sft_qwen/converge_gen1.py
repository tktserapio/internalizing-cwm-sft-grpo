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
    src, dst = action.split(" to ")[1].split(",")
    src_row, src_col = map(int, src.split(","))
    dst_row, dst_col = map(int, dst.split(","))

    # Check if the source and destination are within the board bounds
    if not (0 <= src_row < 5 and 0 <= src_col < 5 and 0 <= dst_row < 5 and 0 <= dst_col < 5):
        return False

    # Check if the source and destination squares are empty
    if state.get(f"{src_row},{src_col}") != '0' and state.get(f"{dst_row},{dst_col}") != '0':
        return False

    # Check if the destination square is adjacent to an opponent's unit
    opponent_units = [unit for unit in state.values() if unit == '1']
    for opp_unit in opponent_units:
        opp_row, opp_col = map(int, opp_unit.split(",")[1:])
        if abs(src_row - opp_row) + abs(src_col - opp_col) == 1:
            return True

    return False

def apply_action(state: State, action: Action) -> State:
    """Apply the given action to the state and return the new state."""
    new_state = copy.deepcopy(state)
    # Extract source and destination coordinates from the action string
    src, dst = action.split(" to ")[1].split(",")
    src_row, src_col = map(int, src.split(","))
    dst_row, dst_col = map(int, dst.split(","))

    # Update the source square with the empty value
    new_state[f"{src_row},{src_col}"] = '0'
    # Update the destination square with the unit's value
    new_state[f"{dst_row},{dst_col}"] = state[f"{src_row},{src_col}"]

    # Remove the unit from its original position
    del new_state[f"{src_row},{src_col}"]
    return new_state

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    initial_state = {
        "0,0": "0",  # Blue unit at (0, 0)
        "0,4": "0",  # Blue unit at (0, 4)
        "1,0": "1",  # Red unit at (4, 0)
        "1,4": "1",  # Red unit at (4, 4)
        "2,2": "0"   # Center square (2, 2) initially empty
    }
    return initial_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    blue_units = [unit for unit in state.values() if unit == '0']
    red_units = [unit for unit in state.values() if unit == '1']
    if len(blue_units) > 0:
        return 0
    elif len(red_units) > 0:
        return 1
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == 0:
        return "Blue"
    elif player_id == 1:
        return "Red"
    else:
        return "Unknown"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if get_current_player(state) == -4:
        return [0.0, 0.0]
    else:
        return [1.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    if current_player == -4:
        return []  # Terminal state
    else:
        legal_actions = []
        for unit in state.values():
            if unit == '0':  # Blue unit
                for i in range(5):
                    for j in range(5):
                        if state.get(f"{i},{j}") == '0':
                            for k in range(5):
                                for l in range(5):
                                    if state.get(f"{k},{l}") == '1':
                                        if is_valid_move(f"{i},{j} to {k},{l}", state):
                                            legal_actions.append(f"move {i},{j} to {k},{l}")
            elif unit == '1':  # Red unit
                for i in range(5):
                    for j in range(5):
                        if state.get(f"{i},{j}") == '1':
                            for k in range(5):
                                for l in range(5):
                                    if state.get(f"{k},{l}") == '0':
                                        for m in range(5):
                                            for n in range(5):
                                                if state.get(f"{m},{n}") == '0':
                                                    if is_valid_move(f"{i},{j} to {m},{n}", state):
                                                        legal_actions.append(f"move {i},{j} to {m},{n}")
        return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {}
    player_1_obs = {}
    for row in range(5):
        for col in range(5):
            if state.get(f"{row},{col}") == '0':
                player_0_obs[f"{row},{col}"] = "Blue"
            elif state.get(f"{row},{col}") == '1':
                player_1_obs[f"{row},{col}"] = "Red"
    return [player_0_obs, player_1_obs]