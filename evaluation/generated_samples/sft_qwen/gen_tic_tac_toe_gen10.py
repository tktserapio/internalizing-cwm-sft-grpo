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
        "is_draw": False
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
    state["current_player"] = 1 - state["current_player"]
    
    # Check for win condition
    if check_win(state):
        state["winner"] = state["current_player"]
        state["is_draw"] = False
        return state
    
    # Check for draw condition
    if all(all(cell != "." for cell in row) for row in state["board"]):
        state["winner"] = None
        state["is_draw"] = True
        return state
    
    return state

def check_win(state: State) -> bool:
    """
    Checks if there is a winning line of four marks for the current player.
    """
    directions = [
        ((0, 0), (0, 1), (0, 2), (0, 3)),  # Horizontal
        ((1, 0), (2, 0), (3, 0), (4, 0)),  # Horizontal
        ((0, 1), (1, 1), (2, 1), (3, 1)),  # Horizontal
        ((0, 2), (1, 2), (2, 2), (3, 2)),  # Horizontal
        ((0, 3), (1, 3), (2, 3), (3, 3)),  # Horizontal
        ((0, 0), (1, 1), (2, 2), (3, 3)),  # Diagonal
        ((0, 3), (1, 2), (2, 1), (3, 0))   # Diagonal
    ]
    
    for direction in directions:
        for i in range(2):  # Check both directions
            for r, c in direction:
                if state["board"][r][c] != "x" if state["current_player"] == 0 else "o":
                    break
            else:
                continue
            break
        else:
            continue
        break
    else:
        return False
    
    return True

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
    if state["winner"] is not None:
        return [-1.0, 1.0] if state["winner"] == 0 else [1.0, -1.0]
    elif state["is_draw"]:
        return [0.0, 0.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state["winner"] is not None or state["is_draw"]:
        return []
    
    return ["{},{}".format(r, c) for r in range(6) for c in range(6) if state["board"][r][c] == "."]

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    observations = []
    for player_id in range(2):
        board = state["board"].copy()
        for r in range(6):
            for c in range(6):
                if board[r][c] == "x" if player_id == 0 else "o":
                    board[r][c] = 1
                else:
                    board[r][c] = 0
        observations.append({
            "board": board,
            "current_player": player_id
        })
    return observations