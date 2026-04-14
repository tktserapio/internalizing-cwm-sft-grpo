import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to initialize the board state
def _init_board(size: int) -> State:
    """Initialize the board state with given size."""
    board = {}
    for i in range(1, size * (size + 1) // 2 + 1):
        board[f"{chr(ord('A') + (i - 1) // (size + 1))}{(i - 1) % (size + 1) + 1}"] = 0
    return board

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    size = 4
    return _init_board(size)

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    new_state[action] = 1  # Mark the cell as occupied by the current player
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    # Assuming the first player is Black (0) and the second player is White (1)
    # In a real implementation, this would be determined based on the turn count
    return 0 if len([action for action in state.keys() if state[action] == 1]) % 2 == 0 else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In a real implementation, this would calculate the score based on the board state
    # For simplicity, we assume a win for the first player
    return [1.0, 0.0] if get_current_player(state) == 0 else [0.0, 1.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    # Legal actions are all unoccupied cells
    return [cell for cell in state.keys() if state[cell] == 0]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    # Observations are the same for both players
    return [{cell: state[cell] for cell in state.keys()} for _ in range(2)]