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
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Convert action string to row, col
    row, col = map(int, action.split(","))
    
    # Check if the action is valid
    if state["board"][row][col] != ".":
        raise ValueError("Cell already occupied")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = (state["current_player"] + 1) % 2
    
    # Check for win condition
    for direction in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        check_winner(state, row, col, direction)
    
    # Check for draw condition
    if all(cell != "." for row in state["board"] for cell in row):
        state["winner"] = "draw"
        state["game_over"] = True
    
    return state

def check_winner(state: State, row: int, col: int, direction: Tuple[int, int]) -> None:
    """
    Checks for a winning line of four marks in a given direction.
    """
    count = 1
    for i in range(1, 4):
        next_row, next_col = row + i * direction[0], col + i * direction[1]
        if 0 <= next_row < 6 and 0 <= next_col < 6 and state["board"][next_row][next_col] == state["board"][row][col]:
            count += 1
        else:
            break
    if count >= 4:
        state["winner"] = state["board"][row][col]
        state["game_over"] = True

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    if state["winner"] == "draw":
        return [0.0, 0.0]
    elif state["winner"] == "x":
        return [1.0, 0.0]
    elif state["winner"] == "o":
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state["game_over"]:
        return []
    else:
        return [f"{row},{col}" for row in range(6) for col in range(6) if state["board"][row][col] == "."]

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    observations = []
    for player_id in range(2):
        observation = {}
        observation["board"] = state["board"]
        observation["current_player"] = get_current_player(state)
        observation["winner"] = state["winner"]
        observation["game_over"] = state["game_over"]
        observation["player_id"] = player_id
        observations.append(observation)
    return observations