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

# Helper function to initialize the board
def _init_board(size: int) -> State:
    """Initialize the board state with given size."""
    board = {}
    for i in range(1, size * (size + 1) // 2 + 1):
        board[f"{chr(ord('A') + (i - 1) // (size + 1))}{(i - 1) % (size + 1) + 1}"] = {"color": None}
    return board

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    size = 4
    return _init_board(size)

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    new_state[action]["color"] = "B" if new_state[action]["color"] == "W" else "W"
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    for _, value in state.items():
        if value["color"] == "B":
            return 0
        elif value["color"] == "W":
            return 1
    return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In a perfect information game like Y, there's no need to track running rewards.
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for cell, value in state.items():
        if value["color"] is None:
            legal_actions.append(cell)
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    for player_id in [0, 1]:
        player_obs = {}
        for cell, value in state.items():
            if value["color"] == "B" if player_id == 0 else "W":
                player_obs[cell] = value["color"]
        observations.append(player_obs)
    return observations