import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants for the game
BOARD_SIZE = 5
CENTER_SQUARE = (2, 2)
MAX_TURNS = 50

# Helper function to create a deep copy of the state
def copy_state(state: State) -> State:
    return {
        "board": [row[:] for row in state["board"]],
        "current_player": state["current_player"],
        "turn_count": state["turn_count"],
        "stunned": [stunned[:] for stunned in state["stunned"]]
    }

# Initialize the game state
def get_initial_state() -> State:
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    board[0][0] = 0
    board[0][4] = 0
    board[4][0] = 1
    board[4][4] = 1
    return {
        "board": board,
        "current_player": 0,
        "turn_count": 0,
        "stunned": [[False for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = copy_state(state)
    if action == "pass":
        new_state["current_player"] = 1 - new_state["current_player"]
        new_state["turn_count"] += 1
        return new_state

    # Parse the action
    parts = action.split()
    r1, c1 = map(int, parts[1][1:-1].split(','))
    r2, c2 = map(int, parts[3][1:-1].split(','))

    # Move the unit
    player = new_state["board"][r1][c1]
    new_state["board"][r1][c1] = None
    new_state["board"][r2][c2] = player

    # Check for stuns
    opponent = 1 - player
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = r2 + dr, c2 + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if new_state["board"][nr][nc] == opponent:
                    new_state["stunned"][nr][nc] = True

    # Clear stuns for current player
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if new_state["board"][r][c] == player:
                new_state["stunned"][r][c] = False

    # Update turn and player
    new_state["current_player"] = opponent
    new_state["turn_count"] += 1

    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    if state["turn_count"] >= MAX_TURNS:
        return -4  # Terminal state due to draw
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if state["board"][r][c] is not None and (r, c) == CENTER_SQUARE:
                return -4  # Terminal state due to victory
    return state["current_player"]

# Get the player name
def get_player_name(player_id: int) -> str:
    return "Blue" if player_id == 0 else "Red"

# Get the rewards for the current state
def get_rewards(state: State) -> List[float]:
    if state["turn_count"] >= MAX_TURNS:
        return [0.5, 0.5]  # Draw
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if state["board"][r][c] is not None and (r, c) == CENTER_SQUARE:
                winner = state["board"][r][c]
                return [1.0, 0.0] if winner == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if get_current_player(state) == -4:
        return []  # No legal actions in terminal state

    legal_actions = []
    player = state["current_player"]

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if state["board"][r][c] == player and not state["stunned"][r][c]:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and state["board"][nr][nc] is None:
                            legal_actions.append(f"move ({r},{c}) to ({nr},{nc})")

    if not legal_actions:
        legal_actions.append("pass")

    return legal_actions

# Get observations for both players
def get_observations(state: State) -> List[PlayerObservation]:
    return [state, state]