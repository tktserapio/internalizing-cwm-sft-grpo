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

# Helper function to check if a player has won
def check_win(board, player):
    # Check rows
    for row in range(6):
        if all(board[f"{row},{col}"] == player for col in range(6)):
            return True
    # Check columns
    for col in range(6):
        if all(board[f"{row},{col}"] == player for row in range(6)):
            return True
    # Check diagonals
    for i in range(3):  # Only need to check up to 3 because we're looking for 4 in a row
        if all(board[f"{i+idx},{i+idx}"] == player for idx in range(4)):
            return True
        if all(board[f"{i+idx},{5-i-idx}"] == player for idx in range(4)):
            return True
    return False

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": {f"{row},{col}": " " for row in range(6) for col in range(6)},
        "current_player": 0,
        "winner": None,
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    row, col = map(int, action.split(","))
    if state["board"][f"{row},{col}"] == " ":
        new_state["board"][f"{row},{col}"] = "x" if new_state["current_player"] == 0 else "o"
        new_state["current_player"] = 1 - new_state["current_player"]
        if check_win(new_state["board"], "x"):
            new_state["winner"] = "x"
            new_state["game_over"] = True
        elif check_win(new_state["board"], "o"):
            new_state["winner"] = "o"
            new_state["game_over"] = True
        elif all(new_state["board"][cell] != " " for cell in new_state["board"]):
            new_state["game_over"] = True
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 1" if player_id == 0 else "Player 2"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["game_over"]:
        if state["winner"] == "x":
            return [1.0, -1.0]
        elif state["winner"] == "o":
            return [-1.0, 1.0]
        else:
            return [0.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    return [f"{row},{col}" for row in range(6) for col in range(6) if state["board"][f"{row},{col}"] == " "]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    for player_id in range(2):
        observation = {}
        for cell, mark in state["board"].items():
            if mark != " ":
                observation[cell] = mark
        observations.append(observation)
    return observations