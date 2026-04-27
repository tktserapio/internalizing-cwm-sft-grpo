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

# Helper function to determine if a position is within the board
def is_within_board(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

# Helper function to get adjacent positions
def get_adjacent_positions(row: int, col: int) -> List[Tuple[int, int]]:
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),         (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    return [(row + dr, col + dc) for dr, dc in directions if is_within_board(row + dr, col + dc)]

# Initialize the game state
def get_initial_state() -> State:
    return {
        "board": {
            (0, 0): 0, (0, 4): 0,
            (4, 0): 1, (4, 4): 1
        },
        "stunned": {
            0: set(),
            1: set()
        },
        "current_player": 0,
        "turns": 0
    }

# Apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    new_state = {
        "board": state["board"].copy(),
        "stunned": {0: state["stunned"][0].copy(), 1: state["stunned"][1].copy()},
        "current_player": state["current_player"],
        "turns": state["turns"] + 1
    }
    
    if action.startswith("move"):
        _, from_pos, _, to_pos = action.split()
        from_pos = tuple(map(int, from_pos.strip("()").split(",")))
        to_pos = tuple(map(int, to_pos.strip("()").split(",")))
        
        player = state["current_player"]
        new_state["board"].pop(from_pos)
        new_state["board"][to_pos] = player
        
        # Update stun status
        opponent = 1 - player
        new_state["stunned"][opponent] = set()
        for adj in get_adjacent_positions(*to_pos):
            if adj in new_state["board"] and new_state["board"][adj] == opponent:
                new_state["stunned"][opponent].add(adj)
    
    new_state["current_player"] = 1 - state["current_player"]
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    if state["turns"] >= MAX_TURNS:
        return -4  # Terminal state due to draw
    for pos, player in state["board"].items():
        if pos == CENTER_SQUARE:
            return -4  # Terminal state due to victory
    return state["current_player"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return "Blue" if player_id == 0 else "Red"

# Get rewards for the players
def get_rewards(state: State) -> List[float]:
    for pos, player in state["board"].items():
        if pos == CENTER_SQUARE:
            return [1.0, -1.0] if player == 0 else [-1.0, 1.0]
    if state["turns"] >= MAX_TURNS:
        return [0.5, 0.5]  # Draw
    return [0.0, 0.0]

# Get legal actions for the current player
def get_legal_actions(state: State) -> List[Action]:
    if get_current_player(state) == -4:
        return []
    
    player = state["current_player"]
    legal_actions = []
    
    for pos, p in state["board"].items():
        if p == player and pos not in state["stunned"][player]:
            for adj in get_adjacent_positions(*pos):
                if adj not in state["board"]:
                    legal_actions.append(f"move {pos} to {adj}")
    
    if not legal_actions:
        legal_actions.append("pass")
    
    return legal_actions

# Get observations for the players
def get_observations(state: State) -> List[PlayerObservation]:
    return [state, state]