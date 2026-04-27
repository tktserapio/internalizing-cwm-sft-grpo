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

# Helper function to initialize the board
def initialize_board() -> List[List[int]]:
    board = [[-1 for _ in range(5)] for _ in range(5)]
    board[0][0] = 0
    board[0][4] = 0
    board[4][0] = 1
    board[4][4] = 1
    return board

# Helper function to get adjacent positions
def get_adjacent_positions(r: int, c: int) -> List[Tuple[int, int]]:
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),         (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    return [(r + dr, c + dc) for dr, dc in directions if 0 <= r + dr < 5 and 0 <= c + dc < 5]

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": initialize_board(),
        "current_player": 0,
        "stunned": {0: [], 1: []},
        "turn_count": 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        "board": [row[:] for row in state["board"]],
        "current_player": state["current_player"],
        "stunned": {0: state["stunned"][0][:], 1: state["stunned"][1][:]},
        "turn_count": state["turn_count"]
    }
    
    if action == "pass":
        new_state["current_player"] = 1 - state["current_player"]
        new_state["turn_count"] += 1
        return new_state

    # Parse the move action
    _, from_pos, _, to_pos = action.split()
    r1, c1 = map(int, from_pos.strip("()").split(","))
    r2, c2 = map(int, to_pos.strip("()").split(","))

    # Move the unit
    player = state["current_player"]
    new_state["board"][r1][c1] = -1
    new_state["board"][r2][c2] = player

    # Update stunned status
    opponent = 1 - player
    new_state["stunned"][opponent] = []

    for adj_r, adj_c in get_adjacent_positions(r2, c2):
        if new_state["board"][adj_r][adj_c] == opponent:
            new_state["stunned"][opponent].append((adj_r, adj_c))

    # Change turn
    new_state["current_player"] = opponent
    new_state["turn_count"] += 1

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["board"][2][2] != -1:
        return -4
    if state["turn_count"] >= 50:
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Blue" if player_id == 0 else "Red"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["board"][2][2] == 0:
        return [1.0, 0.0]
    elif state["board"][2][2] == 1:
        return [0.0, 1.0]
    elif state["turn_count"] >= 50:
        return [0.5, 0.5]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if get_current_player(state) == -4:
        return []

    player = state["current_player"]
    legal_actions = []
    stunned_positions = state["stunned"][player]

    for r in range(5):
        for c in range(5):
            if state["board"][r][c] == player and (r, c) not in stunned_positions:
                for adj_r, adj_c in get_adjacent_positions(r, c):
                    if state["board"][adj_r][adj_c] == -1:
                        legal_actions.append(f"move ({r},{c}) to ({adj_r},{adj_c})")

    if not legal_actions:
        legal_actions.append("pass")

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]