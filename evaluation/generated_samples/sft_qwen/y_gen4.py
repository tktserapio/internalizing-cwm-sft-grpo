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

# Helper function to create a state dictionary
def create_state(board_size: int) -> State:
    """Create an initial state for the game of Y."""
    board = {}
    for i in range(1, board_size * (board_size + 1) // 2 + 1):
        board[f"{i}"] = {"color": None, "is_corner": False}
    return board

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return create_state(4)

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
    # Assuming player 0 is Black and player 1 is White
    # We can track the player's turn using a counter
    turn_counter = 0
    for cell in state.values():
        if cell["color"] is not None:
            turn_counter += 1
    if turn_counter % 2 == 0:
        return 0  # Black's turn
    else:
        return 1  # White's turn

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In this simple implementation, we assume the game ends when one player wins
    # and the other loses. Thus, we return [1.0, -1.0] for a win/loss situation.
    black_wins = sum(cell["color"] == "B" for cell in state.values())
    white_wins = sum(cell["color"] == "W" for cell in state.values())
    if black_wins > white_wins:
        return [1.0, -1.0]
    elif white_wins > black_wins:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    # Legal actions are all empty cells
    legal_actions = []
    for cell_id in state.keys():
        if state[cell_id]["color"] is None:
            legal_actions.append(cell_id)
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    # Observations are the same for both players
    observations = []
    for cell_id in state.keys():
        observation = {
            "cell_id": cell_id,
            "color": state[cell_id]["color"],
            "is_corner": state[cell_id]["is_corner"]
        }
        observations.append(observation)
    return observations