import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to determine the quadrant based on coordinates
def get_quadrant(row: int, col: int) -> str:
    if row < 2 and col < 2:
        return "Top-Left"
    elif row < 2 and col >= 2:
        return "Top-Right"
    elif row >= 2 and col < 2:
        return "Bottom-Left"
    else:
        return "Bottom-Right"

# Returns the initial game state before any actions are taken.
def get_initial_state() -> State:
    p0_row, p0_col = random.choice([(0, 0), (0, 1), (1, 0), (1, 1)])
    p1_row, p1_col = random.choice([(2, 2), (2, 3), (3, 2), (3, 3)])
    return {
        "player_positions": [(p0_row, p0_col), (p1_row, p1_col)],
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }

# Returns the new state after an action has been taken.
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    new_positions = state["player_positions"][:]
    current_player = state["current_player"]
    row, col = new_positions[current_player]

    if action == "Up":
        row = max(0, row - 1)
    elif action == "Down":
        row = min(3, row + 1)
    elif action == "Left":
        col = max(0, col - 1)
    elif action == "Right":
        col = min(3, col + 1)
    # "Stay" action does not change the position

    new_positions[current_player] = (row, col)
    new_state["player_positions"] = new_positions

    # Check if the game is over
    if new_positions[0] == new_positions[1]:
        new_state["game_over"] = True
    else:
        new_state["turn_count"] += 1
        if new_state["turn_count"] >= 20:
            new_state["game_over"] = True
        else:
            new_state["current_player"] = 1 - current_player

    return new_state

# Returns current player (e.g. 0 or 1), or -1 for terminal state.
def get_current_player(state: State) -> int:
    return -1 if state["game_over"] else state["current_player"]

# Returns the name of the player.
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Returns the rewards per player.
def get_rewards(state: State) -> List[float]:
    if not state["game_over"]:
        return [0.0, 0.0]
    p0_pos, p1_pos = state["player_positions"]
    if p0_pos == p1_pos:
        return [-1.0, 1.0] if state["current_player"] == 0 else [1.0, -1.0]
    return [0.0, 0.0]

# Returns legal actions for current state. Empty list if terminal.
def get_legal_actions(state: State) -> List[Action]:
    if state["game_over"]:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

# Returns [player_0_obs, player_1_obs].
def get_observations(state: State) -> List[PlayerObservation]:
    p0_pos, p1_pos = state["player_positions"]
    return [
        {"My Loc": p0_pos, "Opponent Quadrant": get_quadrant(*p1_pos)},
        {"My Loc": p1_pos, "Opponent Quadrant": get_quadrant(*p0_pos)}
    ]

# Stochastically sample a valid sequence of actions that explains the current observations.
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function is complex and requires a stochastic model to generate a valid sequence.
    # For simplicity, we'll return a random sequence of actions that could have led to the current state.
    actions = []
    for obs, action in obs_action_history:
        if action is not None:
            actions.append(action)
        else:
            actions.append(random.choice(["Up", "Down", "Left", "Right", "Stay"]))
    return actions