import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
BOARD_SIZE = 5
CENTER_SQUARE = (2, 2)
MAX_TURNS = 50

# Helper function to check if a position is within the board
def is_within_board(r: int, c: int) -> bool:
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

# Helper function to get adjacent positions
def get_adjacent_positions(r: int, c: int) -> List[Tuple[int, int]]:
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    return [(r + dr, c + dc) for dr, dc in directions if is_within_board(r + dr, c + dc)]

# Initialize the game state
def get_initial_state() -> State:
    return {
        "board": {
            (0, 0): 0, (0, 4): 0,
            (4, 0): 1, (4, 4): 1
        },
        "stunned": set(),
        "current_player": 0,
        "turns": 0
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = {
        "board": state["board"].copy(),
        "stunned": state["stunned"].copy(),
        "current_player": state["current_player"],
        "turns": state["turns"]
    }
    
    if action == "pass":
        # Simply change the current player
        new_state["current_player"] = 1 - state["current_player"]
    else:
        # Parse the action string
        _, src, _, dest = action.split()
        r1, c1 = map(int, src.strip("()").split(","))
        r2, c2 = map(int, dest.strip("()").split(","))
        
        # Move the unit
        del new_state["board"][(r1, c1)]
        new_state["board"][(r2, c2)] = state["current_player"]
        
        # Update stunned status
        new_state["stunned"] = set()
        for adj in get_adjacent_positions(r2, c2):
            if adj in new_state["board"] and new_state["board"][adj] != state["current_player"]:
                new_state["stunned"].add(adj)
        
        # Change the current player
        new_state["current_player"] = 1 - state["current_player"]
    
    # Increment turn count
    new_state["turns"] += 1
    
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    if CENTER_SQUARE in state["board"].values():
        return -4  # Terminal state
    if state["turns"] >= MAX_TURNS:
        return -4  # Terminal state
    return state["current_player"]

# Get the player name
def get_player_name(player_id: int) -> str:
    return "Blue" if player_id == 0 else "Red"

# Get rewards for each player
def get_rewards(state: State) -> List[float]:
    if CENTER_SQUARE in state["board"]:
        winner = state["board"][CENTER_SQUARE]
        return [1.0, 0.0] if winner == 0 else [0.0, 1.0]
    if state["turns"] >= MAX_TURNS:
        return [0.5, 0.5]  # Draw
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if get_current_player(state) == -4:
        return []  # Terminal state
    
    player = state["current_player"]
    legal_actions = []
    
    for (r, c), owner in state["board"].items():
        if owner == player and (r, c) not in state["stunned"]:
            for adj in get_adjacent_positions(r, c):
                if adj not in state["board"]:
                    legal_actions.append(f"move ({r},{c}) to ({adj[0]},{adj[1]})")
    
    if not legal_actions:
        legal_actions.append("pass")
    
    return legal_actions

# Get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    return [state, state]  # Perfect information game