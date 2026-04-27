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
    # Convert action string to row, col coordinates
    row, col = map(int, action.split(","))
    
    # Check if the action is valid
    if state["board"][row][col] != ".":
        raise ValueError("Invalid action: Cell already occupied")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = (state["current_player"] + 1) % 2
    
    # Check for win condition
    check_winner(state)
    
    # Check for draw condition
    if all(all(cell != "." for cell in row) for row in state["board"]):
        state["game_over"] = True
    
    return state

def check_winner(state: State) -> None:
    """
    Checks if there is a winner based on the current state of the board.
    """
    # Check horizontal lines
    for row in state["board"]:
        if len(set(row)) == 1 and row[0] != ".":
            state["winner"] = "x" if row[0] == "x" else "o"
            state["game_over"] = True
            return
    
    # Check vertical lines
    for col in range(6):
        if len(set(state["board"][row][col] for row in range(6))) == 1 and state["board"][row][col] != ".":
            state["winner"] = "x" if state["board"][row][col] == "x" else "o"
            state["game_over"] = True
            return
    
    # Check diagonal lines
    for i in range(3):
        if state["board"][i][i] != "." and state["board"][i][i] == state["board"][i+1][i+1] == state["board"][i+2][i+2] == state["board"][i+3][i+3]:
            state["winner"] = "x" if state["board"][i][i] == "x" else "o"
            state["game_over"] = True
            return
        
        if state["board"][i][5-i] != "." and state["board"][i][5-i] == state["board"][i+1][4-i] == state["board"][i+2][3-i] == state["board"][i+3][2-i]:
            state["winner"] = "x" if state["board"][i][5-i] == "x" else "o"
            state["game_over"] = True
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
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state["winner"] == "x":
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
    board_observation = []
    for row in state["board"]:
        board_observation.append("".join(row))
    
    player_0_obs = {"board": board_observation, "turn": "x" if state["current_player"] == 0 else "o"}
    player_1_obs = {"board": board_observation, "turn": "x" if state["current_player"] == 1 else "o"}
    
    return [player_0_obs, player_1_obs]