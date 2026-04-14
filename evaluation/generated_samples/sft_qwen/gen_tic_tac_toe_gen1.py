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
    # Initial state with all cells empty
    return {
        "board": [[" " for _ in range(6)] for _ in range(6)],
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
    if row < 0 or row > 5 or col < 0 or col > 5 or state["board"][row][col] != " ":
        raise ValueError("Invalid action")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = (state["current_player"] + 1) % 2
    
    # Check for win condition
    check_winner(state)
    
    return state

def check_winner(state: State):
    """
    Checks for a winner based on the current state of the board.
    """
    # Check rows and columns
    for i in range(6):
        if state["board"][i][0] != " " and state["board"][i][0] == state["board"][i][1] == state["board"][i][2] == state["board"][i][3]:
            state["winner"] = state["current_player"]
            state["game_over"] = True
        if state["board"][0][i] != " " and state["board"][0][i] == state["board"][1][i] == state["board"][2][i] == state["board"][3][i]:
            state["winner"] = state["current_player"]
            state["game_over"] = True
    
    # Check diagonals
    if state["board"][0][0] != " " and state["board"][0][0] == state["board"][1][1] == state["board"][2][2] == state["board"][3][3]:
        state["winner"] = state["current_player"]
        state["game_over"] = True
    if state["board"][0][5] != " " and state["board"][0][5] == state["board"][1][4] == state["board"][2][3] == state["board"][3][2]:
        state["winner"] = state["current_player"]
        state["game_over"] = True
    
    # Check for draw
    if state["game_over"] is False and all(cell != " " for row in state["board"] for cell in row):
        state["winner"] = None
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
    return "Player 1" if player_id == 0 else "Player 2"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state["winner"] is None:
        return [0.0, 0.0]
    elif state["winner"] == 0:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state["game_over"]:
        return []
    return ["{},{}".format(row, col) for row in range(6) for col in range(6) if state["board"][row][col] == " "]

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