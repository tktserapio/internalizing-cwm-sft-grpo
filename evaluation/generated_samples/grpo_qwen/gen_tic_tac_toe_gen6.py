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
    """
    Returns the initial game state before any actions are taken.
    """
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
        raise ValueError("Cell already occupied")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = (state["current_player"] + 1) % 2
    
    # Increment the turn count
    state["turn_count"] += 1
    
    # Check for win condition
    check_winner(state)
    
    # Check for draw condition
    if state["turn_count"] == 36:
        state["winner"] = "draw"
    
    return state

def check_winner(state: State):
    """
    Checks if there is a winner based on the current state of the board.
    """
    # Check horizontal lines
    for row in state["board"]:
        for i in range(0, 3):
            if row[i] == row[i+1] == row[i+2] == row[i+3] != ".":
                state["winner"] = "x" if row[i] == "x" else "o"
                return
    
    # Check vertical lines
    for col in range(6):
        for i in range(0, 3):
            if state["board"][i][col] == state["board"][i+1][col] == state["board"][i+2][col] == state["board"][i+3][col] != ".":
                state["winner"] = "x" if state["board"][i][col] == "x" else "o"
                return
    
    # Check diagonal lines
    for i in range(3):
        if state["board"][i][i] == state["board"][i+1][i+1] == state["board"][i+2][i+2] == state["board"][i+3][i+3] != ".":
            state["winner"] = "x" if state["board"][i][i] == "x" else "o"
            return
        if state["board"][i][5-i] == state["board"][i+1][4-i] == state["board"][i+2][3-i] == state["board"][i+3][2-i] != ".":
            state["winner"] = "x" if state["board"][i][5-i] == "x" else "o"
            return

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return "Player 1" if player_id == 0 else "Player 2"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    if state["winner"] == "x":
        return [1.0, 0.0]
    elif state["winner"] == "o":
        return [0.0, 1.0]
    elif state["winner"] == "draw":
        return [0.5, 0.5]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state["winner"] is not None:
        return []
    legal_actions = []
    for row in range(6):
        for col in range(6):
            if state["board"][row][col] == ".":
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    observations = []
    for row in state["board"]:
        observation = {"row": row, "turn_count": state["turn_count"], "winner": state["winner"]}
        observations.append(observation)
    return observations