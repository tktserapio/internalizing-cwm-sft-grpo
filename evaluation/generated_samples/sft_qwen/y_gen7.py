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
def _initialize_board(size: int) -> State:
    board = {}
    for i in range(1, size * (size + 1) // 2 + 1):
        board[f"{chr(ord('A') + (i - 1) // (size + 1))}{(i - 1) % (size + 1) + 1}"] = None
    return board

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    size = 4
    board = _initialize_board(size)
    return {"board": board, "current_player": 0}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    cell = f"{action[0]}, {action[1]}"
    new_state["board"][cell] = new_state["current_player"]
    new_state["current_player"] = 1 - new_state["current_player"]
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In this simple implementation, we assume the game ends when the board is full, and the last player to move wins.
    if len(state["board"]) == (state["current_player"] + 1) * (state["current_player"] + 2) // 2:
        return [1.0, 0.0] if state["current_player"] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state["board"]
    legal_actions = []
    for cell in board.keys():
        if board[cell] is None:
            legal_actions.append(cell)
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state["board"]
    observations = []
    for player_id in range(2):
        observation = {}
        for cell in board.keys():
            if board[cell] is None:
                continue
            if board[cell] == player_id:
                observation[cell] = True
            else:
                observation[cell] = False
        observations.append(observation)
    return observations