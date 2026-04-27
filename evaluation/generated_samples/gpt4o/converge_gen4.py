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

# Helper function to create a new 5x5 board
def create_board() -> List[List[int]]:
    return [[-1 for _ in range(5)] for _ in range(5)]

# Helper function to clone the state
def clone_state(state: State) -> State:
    return {
        "board": [row[:] for row in state["board"]],
        "current_player": state["current_player"],
        "stunned": [state["stunned"][0][:], state["stunned"][1][:]],
        "turn_count": state["turn_count"]
    }

# Initialize the game state
def get_initial_state() -> State:
    board = create_board()
    board[0][0] = 0  # Player 0's unit
    board[0][4] = 0  # Player 0's unit
    board[4][0] = 1  # Player 1's unit
    board[4][4] = 1  # Player 1's unit
    return {
        "board": board,
        "current_player": 0,
        "stunned": [[], []],  # List of stunned units per player
        "turn_count": 0
    }

# Apply an action to the state and return a new state
def apply_action(state: State, action: Action) -> State:
    new_state = clone_state(state)
    if action == "pass":
        new_state["current_player"] = 1 - state["current_player"]
        new_state["turn_count"] += 1
        return new_state

    # Parse the action
    parts = action.split()
    r1, c1 = map(int, parts[1].strip("()").split(","))
    r2, c2 = map(int, parts[3].strip("()").split(","))

    # Move the unit
    player = state["current_player"]
    new_state["board"][r1][c1] = -1
    new_state["board"][r2][c2] = player

    # Update stunned status
    opponent = 1 - player
    new_state["stunned"][opponent] = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = r2 + dr, c2 + dc
            if 0 <= nr < 5 and 0 <= nc < 5 and new_state["board"][nr][nc] == opponent:
                new_state["stunned"][opponent].append((nr, nc))

    # Switch player
    new_state["current_player"] = opponent
    new_state["turn_count"] += 1

    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    if state["board"][2][2] != -1:
        return -4  # Terminal state
    if state["turn_count"] >= 50:
        return -4  # Terminal state
    return state["current_player"]

# Get the player name
def get_player_name(player_id: int) -> str:
    return "Blue" if player_id == 0 else "Red"

# Get the rewards for the current state
def get_rewards(state: State) -> List[float]:
    if state["board"][2][2] == 0:
        return [1.0, -1.0]  # Player 0 wins
    elif state["board"][2][2] == 1:
        return [-1.0, 1.0]  # Player 1 wins
    elif state["turn_count"] >= 50:
        return [0.0, 0.0]  # Draw
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if get_current_player(state) == -4:
        return []

    player = state["current_player"]
    legal_actions = []
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for r in range(5):
        for c in range(5):
            if state["board"][r][c] == player and (r, c) not in state["stunned"][player]:
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 5 and 0 <= nc < 5 and state["board"][nr][nc] == -1:
                        legal_actions.append(f"move ({r},{c}) to ({nr},{nc})")

    if not legal_actions:
        legal_actions.append("pass")

    return legal_actions

# Get observations for both players
def get_observations(state: State) -> List[PlayerObservation]:
    return [{"board": state["board"], "current_player": state["current_player"]}] * 2