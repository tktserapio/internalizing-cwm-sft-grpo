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

# Helper function to create a board state dictionary
def create_board(size: int) -> State:
    board = {}
    for i in range(1, size + 1):
        for j in range(1, size + 1):
            if i == j:
                board[f"{i},{j}"] = {"color": None, "type": "corner"}
            elif i + j == size + 1:
                board[f"{i},{j}"] = {"color": None, "type": "corner"}
            else:
                board[f"{i},{j}"] = {"color": None, "type": "empty"}
    return board

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    size = 4
    return create_board(size)

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = 0 if state["current_player"] == "Black" else 1
    new_state[action]["color"] = player_id
    new_state["current_player"] = "White" if player_id == 0 else "Black"
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return int(state["current_player"])

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In this simple implementation, we assume a win for the first player
    return [1.0, 0.0] if state["current_player"] == "Black" else [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    legal_actions = []
    for cell in state:
        if state[cell]["color"] is None:
            legal_actions.append(cell)
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    for player_id in range(2):
        observation = {}
        for cell in state:
            if state[cell]["color"] is not None and state[cell]["color"] == player_id:
                observation[cell] = state[cell]
        observations.append(observation)
    return observations

# Example usage
initial_state = get_initial_state()
print("Initial State:", initial_state)
black_move = "4"
new_state = apply_action(initial_state, black_move)
print("New State after Black's move:", new_state)
print("Current Player:", get_current_player(new_state))
print("Rewards:", get_rewards(new_state))
print("Legal Actions:", get_legal_actions(new_state))
print("Observations:", get_observations(new_state))