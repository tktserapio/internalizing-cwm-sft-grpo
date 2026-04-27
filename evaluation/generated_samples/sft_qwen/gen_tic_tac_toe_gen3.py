import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initialize the board with empty cells
    board = {f"{i},{j}": None for i in range(6) for j in range(6)}
    return {"board": board}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Convert action string to coordinates
    row, col = map(int, action.split(","))
    
    # Check if the action is valid
    if state["board"].get(f"{row},{col}") is not None:
        raise ValueError("Cell is already occupied.")
    
    # Apply the action
    state["board"][action] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = 1 - state["current_player"]
    
    return state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state.get("current_player", -4)

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return "Player 1" if player_id == 0 else "Player 2"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # Check if the game is over
    if not get_legal_actions(state):
        return [1.0, -1.0] if get_current_player(state) == 0 else [-1.0, 1.0]
    
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    # Get the current player's marks
    player_marks = state["board"].values()
    current_player_marks = [mark for mark in player_marks if mark == "x" if state["current_player"] == 0 else "o"]
    
    # Find all possible winning lines
    def find_winning_lines():
        for row in state["board"]:
            if state["board"][row] == "x" * 4 if state["current_player"] == 0 else "o" * 4:
                yield row
        for col in range(6):
            if all(state["board"][f"{i},{col}"] == "x" if state["current_player"] == 0 else "o" for i in range(6)):
                yield f"{col},0" if state["current_player"] == 0 else f"{col},5"
        for diag in [(0, 5), (1, 4), (2, 3)]:
            if all(state["board"][f"{diag[0]+i},{diag[1]-i}"] == "x" if state["current_player"] == 0 else "o" for i in range(4)):
                yield f"{diag[0]},0" if state["current_player"] == 0 else f"{diag[1]},5"
    
    # Remove all marked cells from the legal actions
    return [action for action in ["{row},{col}" for row in range(6) for col in range(6)] if action not in state["board"] and action not in find_winning_lines()]

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Get the current player's marks
    player_marks = state["board"].values()
    current_player_marks = [mark for mark in player_marks if mark == "x" if state["current_player"] == 0 else "o"]
    
    # Create observations
    player_0_obs = {
        "board": {k: v for k, v in state["board"].items()},
        "current_player": state["current_player"],
        "player_marks": current_player_marks,
        "legal_actions": get_legal_actions(state)
    }
    
    player_1_obs = {
        "board": {k: v for k, v in state["board"].items()},
        "current_player": state["current_player"],
        "player_marks": [mark for mark in player_marks if mark != "x" if state["current_player"] == 0 else "o"],
        "legal_actions": get_legal_actions(state)
    }
    
    return [player_0_obs, player_1_obs]