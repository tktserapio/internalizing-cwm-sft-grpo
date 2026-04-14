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

# Helper function to create an initial state
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [["." for _ in range(6)] for _ in range(6)],
        "current_player": 0,
        "winner": None,
        "game_over": False
    }

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Convert action to row and column
    row, col = map(int, action.split(","))
    
    # Check if the action is valid
    if state["board"][row][col] != ".":
        raise ValueError("Cell already occupied")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = 1 if state["current_player"] == 0 else 0
    
    # Check for win condition
    if check_win(state):
        state["winner"] = state["current_player"]
        state["game_over"] = True
    
    return state

# Function to check if there is a winner
def check_win(state: State) -> bool:
    """
    Checks if any player has won the game based on the current state.
    """
    # Check rows and columns
    for i in range(6):
        if state["board"][i][0] != "." and \
           state["board"][i][0] == state["board"][i][1] == state["board"][i][2] == state["board"][i][3]:
            return True
        if state["board"][0][i] != "." and \
           state["board"][0][i] == state["board"][1][i] == state["board"][2][i] == state["board"][3][i]:
            return True
    
    # Check diagonals
    if state["board"][0][0] != "." and \
       state["board"][0][0] == state["board"][1][1] == state["board"][2][2] == state["board"][3][3]:
        return True
    if state["board"][0][5] != "." and \
       state["board"][0][5] == state["board"][1][4] == state["board"][2][3] == state["board"][3][2]:
        return True
    
    return False

# Function to get the current player
def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

# Function to get the player name
def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 1" if player_id == 0 else "Player 2"

# Function to get rewards
def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["game_over"]:
        if state["winner"] is None:
            return [0.0, 0.0]
        elif state["winner"] == 0:
            return [1.0, -1.0]
        else:
            return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

# Function to get legal actions
def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    else:
        legal_actions = []
        for row in range(6):
            for col in range(6):
                if state["board"][row][col] == ".":
                    legal_actions.append(f"{row},{col}")
        return legal_actions

# Function to get observations
def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    # Since it's a perfect information game, both players see the same state
    return [
        {
            "board": state["board"],
            "current_player": get_current_player(state),
            "winner": state["winner"],
            "game_over": state["game_over"]
        },
        {
            "board": state["board"],
            "current_player": get_current_player(state),
            "winner": state["winner"],
            "game_over": state["game_over"]
        }
    ]