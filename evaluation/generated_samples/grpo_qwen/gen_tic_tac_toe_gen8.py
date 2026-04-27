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
    # Parse the action
    row, col = map(int, action.split(","))
    
    # Check if the action is valid
    if state["board"][row][col] != ".":
        raise ValueError("Cell already occupied")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = (state["current_player"] + 1) % 2
    
    # Check for win condition
    for direction in [
        ((row, col), (row, col+3)), ((row, col+1), (row, col+4)), ((row, col+2), (row, col+5)),
        ((row, col), (row+3, col)), ((row+1, col), (row+4, col)), ((row+2, col), (row+5, col)),
        ((row, col), (row+3, col+3)), ((row+1, col), (row+4, col+4)), ((row+2, col), (row+5, col+5)),
        ((row, col), (row+3, col-3)), ((row+1, col), (row+4, col-4)), ((row+2, col), (row+5, col-5))
    ]:
        start, end = direction
        if all(state["board"][start[0]][start[1]] == state["board"][end[0]][end[1]] == "x" for start, end in zip(start, end)):
            state["winner"] = 0
            state["game_over"] = True
        elif all(state["board"][start[0]][start[1]] == state["board"][end[0]][end[1]] == "o" for start, end in zip(start, end)):
            state["winner"] = 1
            state["game_over"] = True
            
    # Check for draw
    if not state["game_over"]:
        if all(cell != "." for row in state["board"] for cell in row):
            state["winner"] = None
            state["game_over"] = True
    
    return state

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
    if state["winner"] == 0:
        return [1.0, 0.0]
    elif state["winner"] == 1:
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
    for player_id, player_board in enumerate(state["board"]):
        observation = {"board": player_board, "current_player": get_current_player(state)}
        observations.append(observation)
    return observations