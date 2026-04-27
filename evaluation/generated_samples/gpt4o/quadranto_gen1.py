import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

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

# Returns the initial game state before any actions are taken.
def get_initial_state() -> State:
    state = {
        "player_positions": [(0, 0), (3, 3)],  # P0 starts in Q1, P1 in Q4
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }
    return state

# Returns the new state after an action has been taken.
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if new_state["game_over"]:
        return new_state

    player = new_state["current_player"]
    row, col = new_state["player_positions"][player]

    # Update position based on action
    if action == "Up":
        row = max(0, row - 1)
    elif action == "Down":
        row = min(3, row + 1)
    elif action == "Left":
        col = max(0, col - 1)
    elif action == "Right":
        col = min(3, col + 1)
    # "Stay" does not change the position

    new_state["player_positions"][player] = (row, col)

    # Check for win condition
    if new_state["player_positions"][0] == new_state["player_positions"][1]:
        new_state["game_over"] = True
    else:
        # Increment turn count and switch player
        new_state["turn_count"] += 1
        if new_state["turn_count"] >= 20:
            new_state["game_over"] = True
        else:
            new_state["current_player"] = 1 - player

    return new_state

# Returns current player (e.g. 0 or 1), or -4 for terminal state.
def get_current_player(state: State) -> int:
    return -4 if state["game_over"] else state["current_player"]

# Returns the name of the player.
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Returns the rewards per player.
def get_rewards(state: State) -> List[float]:
    if not state["game_over"]:
        return [0.0, 0.0]
    
    if state["player_positions"][0] == state["player_positions"][1]:
        winner = 1 - state["current_player"]
        return [1.0 if winner == 0 else -1.0, 1.0 if winner == 1 else -1.0]
    return [0.0, 0.0]

# Returns legal actions for current state. Empty list if terminal.
def get_legal_actions(state: State) -> List[Action]:
    if state["game_over"]:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

# Returns [player_0_obs, player_1_obs].
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

# Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    actions = []
    state = get_initial_state()
    for obs, action in obs_action_history:
        if action is not None:
            actions.append(action)
            state = apply_action(state, action)
    return actions