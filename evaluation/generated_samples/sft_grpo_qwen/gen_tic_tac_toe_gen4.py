import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [["." for _ in range(6)] for _ in range(6)],
        "current_player": 0,
        "winner": None,
        "turn_count": 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Parse the action
    row, col = map(int, action.split(","))
    
    # Check if the action is valid
    if state["board"][row][col] != ".":
        raise ValueError("Cell is already occupied.")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = (state["current_player"] + 1) % 2
    
    # Increment the turn count
    state["turn_count"] += 1
    
    # Check for win condition
    if check_win(state):
        state["winner"] = state["current_player"]
    
    # Check for draw condition
    if state["turn_count"] == 36:
        state["winner"] = None
    
    return state

def check_win(state: State) -> bool:
    """
    Checks if there is a winning line of four marks for the current player.
    """
    directions = [
        ((0, 0), (0, 1), (0, 2), (0, 3)),  # Horizontal
        ((1, 0), (1, 1), (1, 2), (1, 3)),  # Horizontal
        ((2, 0), (2, 1), (2, 2), (2, 3)),  # Horizontal
        ((3, 0), (3, 1), (3, 2), (3, 3)),  # Horizontal
        ((0, 0), (1, 0), (2, 0), (3, 0)),  # Vertical
        ((0, 1), (1, 1), (2, 1), (3, 1)),  # Vertical
        ((0, 2), (1, 2), (2, 2), (3, 2)),  # Vertical
        ((0, 3), (1, 3), (2, 3), (3, 3)),  # Vertical
        ((0, 0), (1, 1), (2, 2), (3, 3)),  # Diagonal
        ((0, 3), (1, 2), (2, 1), (3, 0))   # Diagonal
    ]
    
    for direction in directions:
        for i in range(6):
            if state["board"][direction[0][0]][i] == state["board"][direction[1][0]][i] == state["board"][direction[2][0]][i] == state["board"][direction[3][0]][i] == "x":
                return True
            elif state["board"][direction[0][0]][i] == state["board"][direction[1][0]][i] == state["board"][direction[2][0]][i] == state["board"][direction[3][0]][i] == "o":
                return True
    return False

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 1" if player_id == 0 else "Player 2"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["winner"] is not None:
        return [1.0, 0.0] if state["winner"] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["winner"] is not None:
        return []
    return ["{},{}".format(row, col) for row in range(6) for col in range(6) if state["board"][row][col] == "."]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {
        "board": state["board"],
        "current_player": state["current_player"],
        "winner": state["winner"],
        "turn_count": state["turn_count"]
    }
    player_1_obs = {
        "board": state["board"],
        "current_player": state["current_player"],
        "winner": state["winner"],
        "turn_count": state["turn_count"]
    }
    return [player_0_obs, player_1_obs]