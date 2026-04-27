import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import itertools

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to create a board state
def create_board(size: int) -> State:
    board = {}
    for i in range(1, size * (size + 1) // 2 + 1):
        board[f"{chr(ord('A') + (i - 1) // (size + 1))}{(i - 1) % (size + 1) + 1}"] = {"color": None}
    return board

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    size = 4
    board = create_board(size)
    return board

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Convert action string to coordinates
    row, col = map(int, action.split(","))
    # Update the board with the action
    state[f"A{col}"] = {"color": 0 if row == 0 else 1}
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    for _, piece in state.items():
        if piece["color"] is not None:
            return piece["color"]
    return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    black_stones = sum(1 for _, piece in state.items() if piece["color"] == 0)
    white_stones = sum(1 for _, piece in state.items() if piece["color"] == 1)
    return [black_stones, white_stones]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for cell in state.keys():
        if state[cell]["color"] is None:
            legal_actions.append(cell)
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    for player_id in range(2):
        observation = {}
        for cell in state.keys():
            if state[cell]["color"] == player_id:
                observation[cell] = state[cell]["color"]
        observations.append(observation)
    return observations

# Example usage
initial_state = get_initial_state()
print("Initial State:", initial_state)

# Apply a move
move = "0,0"
new_state = apply_action(initial_state, move)
print("After Move:", new_state)

# Check current player
current_player = get_current_player(new_state)
print("Current Player:", get_player_name(current_player))

# Get rewards
rewards = get_rewards(new_state)
print("Rewards:", rewards)

# Get legal actions
legal_actions = get_legal_actions(new_state)
print("Legal Actions:", legal_actions)

# Get observations
observations = get_observations(new_state)
print("Observations:", observations)