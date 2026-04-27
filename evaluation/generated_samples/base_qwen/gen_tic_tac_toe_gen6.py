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
    # Convert action string to tuple (row, col)
    row, col = map(int, action.split(","))
    
    # Check if the action is valid
    if state["board"][row][col] != ".":
        raise ValueError("Invalid action: Cell already occupied.")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = 1 if state["current_player"] == 0 else 0
    
    # Check for win condition
    if check_win(state):
        state["winner"] = state["current_player"]
        state["game_over"] = True
    
    return state

def check_win(state: State) -> bool:
    """
    Checks if any player has won the game.
    """
    # Check horizontal lines
    for row in state["board"]:
        if len(set(row)) == 1 and row[0] != ".":
            return True
    
    # Check vertical lines
    for col in range(6):
        if len(set([state["board"][r][col] for r in range(6)])) == 1 and state["board"][0][col] != ".":
            return True
    
    # Check diagonal lines
    for i in range(3):  # Only need to check up to 3 because we're looking for 4 in a row
        if state["board"][i][i] != "." and state["board"][i][i] == state["board"][i+1][i+1] == state["board"][i+2][i+2] == state["board"][i+3][i+3]:
            return True
        if state["board"][i][5-i] != "." and state["board"][i][5-i] == state["board"][i+1][4-i] == state["board"][i+2][3-i] == state["board"][i+3][2-i]:
            return True
    
    return False

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return "x" if player_id == 0 else "o"

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state["game_over"]:
        if state["winner"] == 0:
            return [1.0, 0.0]
        elif state["winner"] == 1:
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]  # Draw
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state["game_over"]:
        return []
    
    legal_actions = []
    for row in range(6):
        for col in range(6):
            if state["board"][row][col] == ".":
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    observations = []
    for i in range(2):
        observation = {}
        observation["board"] = copy.deepcopy(state["board"])
        observation["current_player"] = get_current_player(state)
        observation["legal_actions"] = get_legal_actions(state)
        observation["reward"] = get_rewards(state)[i]
        observations.append(observation)
    return observations