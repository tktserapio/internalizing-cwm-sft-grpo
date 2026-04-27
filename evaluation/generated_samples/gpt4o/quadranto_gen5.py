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

# Helper function to determine the quadrant of a given position
def get_quadrant(row: int, col: int) -> str:
    if row < 2 and col < 2:
        return "Top-Left"
    elif row < 2 and col >= 2:
        return "Top-Right"
    elif row >= 2 and col < 2:
        return "Bottom-Left"
    else:
        return "Bottom-Right"

# Returns the initial game state before any actions are taken
def get_initial_state() -> State:
    state = {
        "player_positions": [(0, 0), (3, 3)],  # Initial positions for P0 and P1
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }
    return state

# Returns the new state after an action has been taken
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if new_state["game_over"]:
        return new_state

    current_player = new_state["current_player"]
    other_player = 1 - current_player
    row, col = new_state["player_positions"][current_player]

    # Determine new position based on action
    if action == "Up":
        row = max(0, row - 1)
    elif action == "Down":
        row = min(3, row + 1)
    elif action == "Left":
        col = max(0, col - 1)
    elif action == "Right":
        col = min(3, col + 1)
    # "Stay" action does not change position

    new_state["player_positions"][current_player] = (row, col)

    # Check for win condition
    if new_state["player_positions"][current_player] == new_state["player_positions"][other_player]:
        new_state["game_over"] = True

    # Update turn count and switch player
    new_state["turn_count"] += 1
    if new_state["turn_count"] >= 20:
        new_state["game_over"] = True
    else:
        new_state["current_player"] = other_player

    return new_state

# Returns current player (e.g. 0 or 1), or -4 for terminal state
def get_current_player(state: State) -> int:
    if state["game_over"]:
        return -4
    return state["current_player"]

# Returns the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Returns the rewards per player
def get_rewards(state: State) -> List[float]:
    if not state["game_over"]:
        return [0.0, 0.0]
    if state["turn_count"] >= 20:
        return [0.0, 0.0]
    winner = state["current_player"]
    loser = 1 - winner
    return [1.0 if winner == 0 else -1.0, 1.0 if winner == 1 else -1.0]

# Returns legal actions for current state
def get_legal_actions(state: State) -> List[Action]:
    if state["game_over"]:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

# Returns [player_0_obs, player_1_obs]
def get_observations(state: State) -> List[PlayerObservation]:
    p0_pos, p1_pos = state["player_positions"]
    p0_obs = {
        "My Loc": p0_pos,
        "Opponent Quadrant": get_quadrant(*p1_pos)
    }
    p1_obs = {
        "My Loc": p1_pos,
        "Opponent Quadrant": get_quadrant(*p0_pos)
    }
    return [p0_obs, p1_obs]

# Stochastically sample a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function is complex and would typically involve reconstructing the game state
    # from the observation history. For simplicity, we'll return an empty list here.
    # Implementing this properly would require a more detailed understanding of the game dynamics.
    return []

# Note: The resample_history function is a placeholder and would require a more detailed implementation
# based on the specific requirements of the game and how the history is tracked.