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

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [["." for _ in range(6)] for _ in range(6)],
        "current_player": 0,
        "winner": None,
        "draw": False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Convert action string to row, col tuple
    row, col = map(int, action.split(","))
    
    # Check if the action is valid
    if state["board"][row][col] != ".":
        raise ValueError("Invalid action: Cell already occupied.")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = (state["current_player"] + 1) % 2
    
    # Check for win condition
    check_winner(state)
    
    # Check for draw condition
    if all(all(cell != "." for cell in row) for row in state["board"]):
        state["draw"] = True
    
    return state

def check_winner(state: State):
    """
    Checks if a player has won the game based on the current board state.
    """
    # Check rows and columns
    for i in range(6):
        if all(state["board"][i][j] == "x" for j in range(6)) or \
           all(state["board"][i][j] == "o" for j in range(6)):
            state["winner"] = 0 if state["board"][i][j] == "x" else 1
            return
        if all(state["board"][j][i] == "x" for j in range(6)) or \
           all(state["board"][j][i] == "o" for j in j in range(6)):
            state["winner"] = 0 if state["board"][j][i] == "x" else 1
            return
    
    # Check diagonals
    if all(state["board"][i][i] == "x" for i in range(6)) or \
       all(state["board"][i][i] == "o" for i in range(6)):
        state["winner"] = 0 if state["board"][i][i] == "x" else 1
        return
    if all(state["board"][i][5-i] == "x" for i in range(6)) or \
       all(state["board"][i][5-i] == "o" for i in range(6)):
        state["winner"] = 0 if state["board"][i][5-i] == "x" else 1
        return

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 1" if player_id == 0 else "Player 2"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["winner"] is not None:
        return [1.0, 0.0] if state["winner"] == 0 else [0.0, 1.0]
    elif state["draw"]:
        return [0.5, 0.5]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["winner"] is not None or state["draw"]:
        return []
    else:
        return [f"{row},{col}" for row in range(6) for col in range(6) if state["board"][row][col] == "."]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {"board": copy.deepcopy(state["board"]), "current_player": state["current_player"]}
    player_1_obs = {"board": copy.deepcopy(state["board"]), "current_player": state["current_player"]}
    return [player_0_obs, player_1_obs]