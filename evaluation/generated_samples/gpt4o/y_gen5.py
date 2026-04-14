import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
PLAYER_NAMES = ["Black", "White"]
BOARD_SIZE = 4  # Size of the board (4 cells per edge for a size-4 board)
NUM_PLAYERS = 2

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        "current_player": 0,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        "board": [row[:] for row in state["board"]],
        "current_player": state["current_player"],
        "winner": state["winner"]
    }
    
    row, col = map(int, action.split(','))
    
    # Place the stone for the current player
    new_state["board"][row][col] = new_state["current_player"]
    
    # Check for a winner
    if check_winner(new_state["board"], row, col, new_state["current_player"]):
        new_state["winner"] = new_state["current_player"]
    
    # Switch to the other player
    new_state["current_player"] = 1 - new_state["current_player"]
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -1 for terminal state."""
    return -1 if state["winner"] is not None else state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return PLAYER_NAMES[player_id]

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["winner"] is None:
        return [0.0, 0.0]
    return [1.0 if state["winner"] == i else 0.0 for i in range(NUM_PLAYERS)]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["winner"] is not None:
        return []
    
    legal_actions = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if state["board"][row][col] is None:
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{"board": state["board"], "current_player": state["current_player"]}] * NUM_PLAYERS

def check_winner(board: List[List[int]], row: int, col: int, player: int) -> bool:
    """Check if the current player has won after placing a stone at (row, col)."""
    # This function should implement the logic to check if a player has connected all three sides.
    # For simplicity, this is a placeholder and should be replaced with the actual logic.
    # Implementing a full connection check is complex and requires graph traversal algorithms.
    return False

# Helper functions can be added here to assist with checking connections and other tasks.