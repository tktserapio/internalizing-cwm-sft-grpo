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

# Helper function to convert coordinates to action string
def coord_to_action(coord: tuple[int, int]) -> Action:
    """Converts (row, col) coordinates to action string."""
    return f"{coord[0]}, {coord[1]}"

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state: empty board
    return {
        "board": {},
        "current_player": 0,
        "size": 4,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    # Convert action string to coordinates
    row, col = map(int, action.split(","))
    
    # Check if action is valid
    if action not in state["board"]:
        state["board"][action] = state["current_player"]
        state["current_player"] = 1 - state["current_player"]
        return state
    
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state["winner"] is not None:
        return [-1.0, 1.0] if state["winner"] == 0 else [1.0, -1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    # Get all possible actions
    legal_actions = []
    for row in range(state["size"] + 1):
        for col in range(state["size"] + 1):
            if coord_to_action((row, col)) not in state["board"]:
                legal_actions.append(coord_to_action((row, col)))
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    # Player 0 sees the full board
    player_0_obs = copy.deepcopy(state)
    player_0_obs["board"] = {coord_to_action(action): player for action, player in player_0_obs["board"].items()}
    
    # Player 1 sees the full board
    player_1_obs = copy.deepcopy(state)
    player_1_obs["board"] = {coord_to_action(action): player for action, player in player_1_obs["board"].items()}
    
    return [player_0_obs, player_1_obs]