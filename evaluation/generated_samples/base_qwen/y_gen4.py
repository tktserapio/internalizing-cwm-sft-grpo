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

# Helper function to generate all possible moves
def generate_possible_moves(board_size):
    """Generates all possible moves for a given board size."""
    moves = []
    for i in range(1, board_size + 1):
        for j in range(1, board_size + 1):
            moves.append(f"{i},{j}")
    return moves

# Required Functions
def get_initial_state(board_size=4):
    """Returns the initial game state before any actions are taken."""
    # Initialize the board with empty cells
    board = {}
    for i in range(1, board_size * (board_size + 1) // 2 + 1):
        board[f"{i}"] = {"color": None, "is_corner": False}
    return board

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    cell_id = action
    new_state[cell_id]["color"] = "B" if new_state[cell_id]["color"] == "W" else "W"
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    # Check if the board is full
    if len(state) == (board_size * (board_size + 1) // 2):
        return -4  # Terminal state
    # Determine the current player based on the turn count
    turn_count = sum(cell["color"] == "B" for cell in state.values())
    return 1 if turn_count % 2 == 0 else 0

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In a perfect information game, there's no need to track running rewards
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    # Generate all possible moves
    possible_moves = generate_possible_moves(len(state))
    # Filter out moves that are already occupied
    legal_moves = [move for move in possible_moves if state.get(move) is None]
    return legal_moves

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    # Since it's a perfect information game, each player sees the exact same state
    observations = [{"board": state, "legal_moves": get_legal_actions(state)} for _ in range(2)]
    return observations

# Example usage
board_size = 4
initial_state = get_initial_state(board_size)
print("Initial State:", initial_state)

# Apply a few actions
state_after_action1 = apply_action(initial_state, "1")
state_after_action2 = apply_action(state_after_action1, "4")
state_after_action3 = apply_action(state_after_action2, "7")
state_after_action4 = apply_action(state_after_action3, "5")
state_after_action5 = apply_action(state_after_action4, "3")
state_after_action6 = apply_action(state_after_action5, "8")

# Get current player and legal actions
current_player = get_current_player(state_after_action6)
print("Current Player:", get_player_name(current_player))

# Get rewards
rewards = get_rewards(state_after_action6)
print("Rewards:", rewards)

# Get legal actions
legal_actions = get_legal_actions(state_after_action6)
print("Legal Actions:", legal_actions)

# Get observations
observations = get_observations(state_after_action6)
print("Observations:", observations)