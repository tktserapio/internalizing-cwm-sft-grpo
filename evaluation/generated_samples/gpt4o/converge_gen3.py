import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
BOARD_SIZE = 5
CENTER_SQUARE = (2, 2)
MAX_TURNS = 50

# Helper function to create a new board
def create_board() -> List[List[int]]:
    return [[-1 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

# Helper function to check if a move is within bounds
def is_within_bounds(r: int, c: int) -> bool:
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

# Helper function to get adjacent squares
def get_adjacent_squares(r: int, c: int) -> List[Tuple[int, int]]:
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    return [(r + dr, c + dc) for dr, dc in directions if is_within_bounds(r + dr, c + dc)]

# Initialize the game state
def get_initial_state() -> State:
    board = create_board()
    board[0][0] = 0
    board[0][4] = 0
    board[4][0] = 1
    board[4][4] = 1
    return {
        "board": board,
        "current_player": 0,
        "turn_count": 0,
        "stunned": {0: [], 1: []}
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = {
        "board": [row[:] for row in state["board"]],
        "current_player": state["current_player"],
        "turn_count": state["turn_count"] + 1,
        "stunned": {0: state["stunned"][0][:], 1: state["stunned"][1][:]}
    }
    
    if action == "pass":
        new_state["current_player"] = 1 - state["current_player"]
        return new_state

    _, src, _, dst = action.split()
    r1, c1 = map(int, src.strip("()").split(","))
    r2, c2 = map(int, dst.strip("()").split(","))

    player = state["current_player"]
    new_state["board"][r1][c1] = -1
    new_state["board"][r2][c2] = player

    # Update stunned units
    opponent = 1 - player
    new_state["stunned"][opponent] = []
    for adj_r, adj_c in get_adjacent_squares(r2, c2):
        if new_state["board"][adj_r][adj_c] == opponent:
            new_state["stunned"][opponent].append((adj_r, adj_c))

    new_state["current_player"] = opponent
    return new_state

# Determine the current player
def get_current_player(state: State) -> int:
    if state["turn_count"] >= MAX_TURNS:
        return -4
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if state["board"][r][c] != -1 and (r, c) == CENTER_SQUARE:
                return -4
    return state["current_player"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return "Blue" if player_id == 0 else "Red"

# Get the rewards for each player
def get_rewards(state: State) -> List[float]:
    if state["turn_count"] >= MAX_TURNS:
        return [0.0, 0.0]
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if state["board"][r][c] != -1 and (r, c) == CENTER_SQUARE:
                winner = state["board"][r][c]
                return [1.0, 0.0] if winner == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if get_current_player(state) == -4:
        return []

    player = state["current_player"]
    legal_actions = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if state["board"][r][c] == player and (r, c) not in state["stunned"][player]:
                for adj_r, adj_c in get_adjacent_squares(r, c):
                    if state["board"][adj_r][adj_c] == -1:
                        legal_actions.append(f"move ({r},{c}) to ({adj_r},{adj_c})")

    if not legal_actions:
        legal_actions.append("pass")

    return legal_actions

# Get observations for both players
def get_observations(state: State) -> List[PlayerObservation]:
    return [state, state]